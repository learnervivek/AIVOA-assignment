import io
import pytest
from pypdf import PdfWriter
from app.services.extractor import (
    extract_text_from_pdf,
    extract_text_from_raw_or_email,
    clean_extracted_text,
    detect_pharma_entities,
    DocumentExtractionError,
)


def create_sample_pdf_bytes(text: str) -> bytes:
    """Helper to generate a minimal valid PDF in-memory with text."""
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    # Write empty PDF or with text
    buffer = io.BytesIO()
    writer.write(buffer)
    # If text is provided, let's create a PDF containing real text stream
    # A standard raw PDF stream with Text
    pdf_content = (
        b"%PDF-1.4\n"
        b"1 0 obj <</Type /Catalog /Pages 2 0 R>> endobj\n"
        b"2 0 obj <</Type /Pages /Kids [3 0 R] /Count 1>> endobj\n"
        b"3 0 obj <</Type /Page /Parent 2 0 R /Resources <</Font <</F1 4 0 R>>>> "
        b"/MediaBox [0 0 612 792] /Contents 5 0 R>> endobj\n"
        b"4 0 obj <</Type /Font /Subtype /Type1 /BaseFont /Helvetica>> endobj\n"
        b"5 0 obj <</Length " + str(len(text) + 40).encode("ascii") + b">> stream\n"
        b"BT /F1 12 Tf 72 712 Td (" + text.encode("latin-1", "replace") + b") Tj ET\n"
        b"endstream\nendobj\n"
        b"xref\n0 6\n"
        b"0000000000 65535 f \n"
        b"0000000009 00000 n \n"
        b"0000000056 00000 n \n"
        b"0000000111 00000 n \n"
        b"0000000238 00000 n \n"
        b"0000000305 00000 n \n"
        b"trailer <</Size 6 /Root 1 0 R>>\n"
        b"startxref\n" + str(450 + len(text)).encode("ascii") + b"\n%%EOF\n"
    )
    return pdf_content


def test_clean_extracted_text():
    raw = "Line 1\r\n\r\n\r\n\r\nLine 2 \t\n  "
    cleaned = clean_extracted_text(raw)
    assert cleaned == "Line 1\n\nLine 2"


def test_detect_pharma_entities():
    sample_text = (
        "Investigation DEV-2026-0891 opened for Atorvastatin batch ATC-2026-0492. "
        "Equipment MILL-PIN-02 showed high temperature. Severity is Critical."
    )
    entities = detect_pharma_entities(sample_text)
    assert "DEV-2026-0891" in entities["deviation_numbers"]
    assert "ATC-2026-0492" in entities["batch_lot_numbers"]
    assert "MILL-PIN-02" in entities["equipment_ids"]
    assert "Critical" in entities["severities"]


def test_extract_text_from_pdf_success():
    sample_text = "Deviation DEV-2026-0042 in Jet Mill MILL-PIN-02. Batch BAT-2026-9901 failed."
    pdf_bytes = create_sample_pdf_bytes(sample_text)
    result = extract_text_from_pdf(pdf_bytes, "deviation_report.pdf")

    assert result["filename"] == "deviation_report.pdf"
    assert result["file_type"] == "pdf"
    assert result["page_count"] >= 1
    assert "DEV-2026-0042" in result["extracted_text"]
    assert "DEV-2026-0042" in result["detected_entities"]["deviation_numbers"]
    assert "BAT-2026-9901" in result["detected_entities"]["batch_lot_numbers"]
    assert "MILL-PIN-02" in result["detected_entities"]["equipment_ids"]


def test_extract_text_from_pdf_empty_file():
    with pytest.raises(DocumentExtractionError) as exc_info:
        extract_text_from_pdf(b"", "empty.pdf")
    assert "empty (0 bytes)" in exc_info.value.message
    assert exc_info.value.status_code == 400


def test_extract_text_from_pdf_invalid_signature():
    with pytest.raises(DocumentExtractionError) as exc_info:
        extract_text_from_pdf(b"This is not a pdf file at all", "fake.pdf")
    assert "missing %PDF header signature" in exc_info.value.message
    assert exc_info.value.status_code == 400


def test_extract_text_from_raw_or_email_with_headers():
    email_text = (
        "From: qa-lead@pharma-api.com\n"
        "To: manufacturing-head@pharma-api.com\n"
        "Date: 2026-11-23 10:15:00\n"
        "Subject: Critical Deviation Alert: DEV-2026-0771 Batch BAT-2026-1200\n\n"
        "Hi Team,\n"
        "Crystallizer REACT-04 suffered cooling jacket glycol leak. Severity is Critical.\n"
        "Batch BAT-2026-1200 has been quarantined."
    )
    result = extract_text_from_raw_or_email(email_text, source_type="email", filename="shift_email.eml")

    assert result["file_type"] == "email"
    assert result["parsed_headers"] is not None
    assert result["parsed_headers"]["from"] == "qa-lead@pharma-api.com"
    assert "Critical Deviation Alert" in result["parsed_headers"]["subject"]
    assert "REACT-04" in result["extracted_text"]
    assert "DEV-2026-0771" in result["detected_entities"]["deviation_numbers"]
    assert "BAT-2026-1200" in result["detected_entities"]["batch_lot_numbers"]
    assert "REACT-04" in result["detected_entities"]["equipment_ids"]
    assert "Critical" in result["detected_entities"]["severities"]


def test_extract_text_from_raw_empty():
    with pytest.raises(DocumentExtractionError) as exc_info:
        extract_text_from_raw_or_email("   ")
    assert "empty" in exc_info.value.message
    assert exc_info.value.status_code == 400
