import io
import re
import logging
import unicodedata
from email import message_from_string
from typing import Dict, Any, Optional, List
from pypdf import PdfReader
from pypdf.errors import PdfReadError

logger = logging.getLogger(__name__)


class DocumentExtractionError(Exception):
    """Custom exception raised when document extraction fails."""
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def clean_extracted_text(text: str) -> str:
    """
    Normalizes Unicode, replaces strange line breaks,
    and strips redundant blank lines while preserving document layout.
    """
    if not text:
        return ""
    # Normalize unicode characters
    normalized = unicodedata.normalize("NFKC", text)
    # Replace non-standard whitespace/tabs
    normalized = normalized.replace("\r\n", "\n").replace("\r", "\n")
    # Collapse 3+ consecutive newlines to 2
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    return normalized.strip()


def detect_pharma_entities(text: str) -> Dict[str, Any]:
    """
    Scans extracted text for common API pharmaceutical & GMP identifiers:
    Deviation Numbers, Batch/Lot Numbers, Equipment Tags, and Severity.
    """
    entities: Dict[str, Any] = {
        "deviation_numbers": [],
        "batch_lot_numbers": [],
        "equipment_ids": [],
        "severities": [],
    }

    if not text:
        return entities

    # Deviation patterns: DEV-2026-001, NC-2026-104, PR-8920
    dev_matches = re.findall(r"\b(?:DEV|NC|CAPA|DR|PR)[-_]\d{4}[-_][A-Za-z0-9]+\b|\bDEV-\d{3,6}\b", text, re.IGNORECASE)
    entities["deviation_numbers"] = list(dict.fromkeys([m.upper() for m in dev_matches]))

    # Batch/Lot patterns: BAT-2026-0881, LOT-99182, ATC-2026-0492, MET-2026-0104 (excluding DEV/NC/PR)
    batch_matches = re.findall(
        r"\b(?:BAT|LOT|BATCH)[-_][A-Za-z0-9\-]+\b|\b(?!DEV|NC|CAPA|DR|PR)[A-Z]{2,4}[-_]\d{4}[-_]\d{3,5}\b",
        text,
        re.IGNORECASE,
    )
    raw_batches = [m.upper() for m in batch_matches if m.upper() not in entities["deviation_numbers"]]
    entities["batch_lot_numbers"] = list(dict.fromkeys(raw_batches))

    # Equipment patterns: MILL-PIN-02, REACT-04, CENT-02, VTD-01, FBD-02, DP-202, DRY-03, TK-101, HPLC-01
    equip_matches = re.findall(
        r"\b(?:MILL|REACT|CENT|DRY|VTD|FBD|FILT|ISO|SIEV|TK|PUMP|VESSEL|DP|TT|PT|HPLC|GC|AHU|HVAC)[-_][A-Za-z0-9\-]+\b",
        text,
        re.IGNORECASE,
    )
    entities["equipment_ids"] = list(dict.fromkeys([m.upper() for m in equip_matches]))

    # Severity keywords
    sev_matches = re.findall(r"\b(Critical|Major|Minor)\b", text, re.IGNORECASE)
    entities["severities"] = list(dict.fromkeys([m.capitalize() for m in sev_matches]))

    return entities


def extract_text_from_pdf(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    """
    Extracts clean text and metadata from an uploaded PDF file.
    Validates PDF integrity, checks for encryption, and handles empty/scanned PDFs.
    """
    file_size_bytes = len(file_bytes)
    if file_size_bytes == 0:
        raise DocumentExtractionError("Uploaded PDF file is empty (0 bytes).", status_code=400)

    # Magic byte check
    if not file_bytes.startswith(b"%PDF"):
        raise DocumentExtractionError(
            f"File '{filename}' is not a valid PDF document (missing %PDF header signature).",
            status_code=400,
        )

    try:
        reader = PdfReader(io.BytesIO(file_bytes))
    except (PdfReadError, Exception) as exc:
        logger.error(f"Failed to parse PDF {filename}: {exc}")
        raise DocumentExtractionError(
            f"Corrupted or malformed PDF file '{filename}': {str(exc)}",
            status_code=422,
        )

    # Check for encryption
    if reader.is_encrypted:
        try:
            decrypted = reader.decrypt("")
            if not decrypted:
                raise DocumentExtractionError(
                    f"PDF file '{filename}' is password protected and cannot be extracted.",
                    status_code=422,
                )
        except Exception:
            raise DocumentExtractionError(
                f"PDF file '{filename}' is encrypted and requires a decryption password.",
                status_code=422,
            )

    page_count = len(reader.pages)
    if page_count == 0:
        raise DocumentExtractionError(
            f"PDF file '{filename}' contains 0 pages.",
            status_code=422,
        )

    page_texts: List[str] = []
    has_text = False

    for idx, page in enumerate(reader.pages, start=1):
        try:
            page_content = page.extract_text() or ""
            cleaned_page = clean_extracted_text(page_content)
            if cleaned_page:
                has_text = True
                if page_count > 1:
                    page_texts.append(f"--- Page {idx} ---\n{cleaned_page}")
                else:
                    page_texts.append(cleaned_page)
        except Exception as exc:
            logger.warning(f"Error extracting text from page {idx} in {filename}: {exc}")

    if not has_text:
        raise DocumentExtractionError(
            f"PDF file '{filename}' contains no extractable text. "
            "It may be a scanned document or image-only PDF without an OCR text layer.",
            status_code=422,
        )

    full_extracted_text = "\n\n".join(page_texts)

    # Extract standard PDF metadata if present
    raw_metadata = reader.metadata or {}
    metadata: Dict[str, Any] = {
        "page_count": page_count,
        "file_size_bytes": file_size_bytes,
        "title": str(raw_metadata.get("/Title", "")).strip() or None,
        "author": str(raw_metadata.get("/Author", "")).strip() or None,
        "subject": str(raw_metadata.get("/Subject", "")).strip() or None,
        "producer": str(raw_metadata.get("/Producer", "")).strip() or None,
    }

    # Detect pharma entities
    detected_entities = detect_pharma_entities(full_extracted_text)

    return {
        "filename": filename,
        "file_type": "pdf",
        "file_size_bytes": file_size_bytes,
        "page_count": page_count,
        "extracted_text": full_extracted_text,
        "metadata": metadata,
        "parsed_headers": None,
        "detected_entities": detected_entities,
    }


def extract_text_from_raw_or_email(
    content: str,
    source_type: str = "text",
    filename: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Parses pasted raw text or email content.
    Extracts headers (Subject, From, Date, To) if formatted as an email or shift log.
    """
    if not content or not content.strip():
        raise DocumentExtractionError("Pasted text content is empty.", status_code=400)

    clean_content = clean_extracted_text(content)
    parsed_headers: Dict[str, str] = {}
    body_text = clean_content

    # Check if content has email/shift-report headers (e.g. Subject: ..., From: ...)
    has_email_headers = any(
        re.search(rf"^{header}:", clean_content, re.MULTILINE | re.IGNORECASE)
        for header in ["Subject", "From", "Date", "To", "Incident Date"]
    )

    if has_email_headers or source_type == "email":
        msg = message_from_string(clean_content)
        header_keys = ["Subject", "From", "To", "Date", "Cc", "Incident-Date", "Severity"]
        for key in header_keys:
            val = msg.get(key)
            if val:
                parsed_headers[key.lower().replace("-", "_")] = val.strip()

        # Extract payload/body
        if msg.is_multipart():
            payload_parts = []
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    payload_parts.append(part.get_payload())
            if payload_parts:
                body_text = "\n".join(payload_parts).strip()
        else:
            payload = msg.get_payload()
            if isinstance(payload, str) and payload.strip():
                body_text = payload.strip()

    detected_entities = detect_pharma_entities(clean_content)

    return {
        "filename": filename or "raw_input.txt",
        "file_type": source_type,
        "file_size_bytes": len(content.encode("utf-8")),
        "page_count": 1,
        "extracted_text": body_text,
        "metadata": {
            "source_type": source_type,
            "character_count": len(clean_content),
            "line_count": len(clean_content.splitlines()),
        },
        "parsed_headers": parsed_headers if parsed_headers else None,
        "detected_entities": detected_entities,
    }
