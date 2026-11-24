import uuid
import logging
from typing import List, Optional, Union
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Query,
    UploadFile,
    File,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, delete
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.investigation import Investigation
from app.models.rca_analysis import RCAAnalysis
from app.models.capa import CAPARecommendation
from app.schemas.investigation import (
    InvestigationCreate,
    InvestigationCreateFull,
    InvestigationUpdate,
    InvestigationUpdateFull,
    InvestigationResponse,
    InvestigationSummaryResponse,
    InvestigationDetailResponse,
)
from app.schemas.extraction import (
    DocumentExtractionResponse,
    RawTextExtractionRequest,
)
from app.services.extractor import (
    extract_text_from_pdf,
    extract_text_from_raw_or_email,
    DocumentExtractionError,
)

logger = logging.getLogger(__name__)

router = APIRouter()


# --------------------------------------------------------------------------
# 1. Document & File Ingestion Endpoints
# --------------------------------------------------------------------------

@router.post(
    "/extract-file",
    response_model=DocumentExtractionResponse,
    status_code=status.HTTP_200_OK,
    summary="Extract clean text and metadata from uploaded PDF",
)
async def extract_file(
    file: UploadFile = File(..., description="Uploaded PDF investigation report or batch record"),
):
    """
    Extracts text, metadata, and detected pharmaceutical entities from an uploaded PDF.
    Validates PDF format, checks for corruption/encryption, and extracts clean text.
    """
    filename = file.filename or "unknown.pdf"
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type for '{filename}'. Only PDF documents (.pdf) are supported.",
        )

    try:
        file_bytes = await file.read()
    except Exception as exc:
        logger.error(f"Failed to read uploaded file '{filename}': {exc}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to read uploaded file content.",
        )

    try:
        result = extract_text_from_pdf(file_bytes=file_bytes, filename=filename)
        return result
    except DocumentExtractionError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)
    except Exception as exc:
        logger.error(f"Unexpected error extracting PDF '{filename}': {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error processing PDF: {str(exc)}",
        )


@router.post(
    "/extract-text",
    response_model=DocumentExtractionResponse,
    status_code=status.HTTP_200_OK,
    summary="Parse raw text or email deviation report",
)
async def extract_text(payload: RawTextExtractionRequest):
    """
    Parses pasted text or email content, extracting headers (Subject, From, Date, To)
    and detected GMP / ICH Q7 entities (deviation number, lot, equipment, severity).
    """
    try:
        result = extract_text_from_raw_or_email(
            content=payload.content,
            source_type=payload.source_type,
            filename=payload.filename,
        )
        return result
    except DocumentExtractionError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)
    except Exception as exc:
        logger.error(f"Unexpected error extracting text: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error processing text: {str(exc)}",
        )


# --------------------------------------------------------------------------
# 2. CRUD Operations for Investigations (Deviation -> RCA -> CAPA)
# --------------------------------------------------------------------------

@router.get(
    "",
    response_model=List[InvestigationSummaryResponse],
    summary="List all investigations with summary fields",
)
async def list_investigations(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    severity: Optional[str] = Query(None, description="Filter by severity: Critical, Major, Minor"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    search: Optional[str] = Query(None, description="Search deviation number, product, or batch"),
    db: AsyncSession = Depends(get_db),
):
    """
    Lists all saved investigations with summary fields:
    (deviation_number, api_product_name, batch_lot_number, severity, status, updated_at).
    """
    query = (
        select(Investigation)
        .options(
            selectinload(Investigation.rca_analyses),
            selectinload(Investigation.capa_recommendations),
        )
        .order_by(Investigation.created_at.desc())
    )

    if severity:
        query = query.where(Investigation.severity == severity)
    if status_filter:
        query = query.where(Investigation.status == status_filter)
    if search:
        search_filter = f"%{search.strip()}%"
        query = query.where(
            or_(
                Investigation.deviation_number.ilike(search_filter),
                Investigation.api_product_name.ilike(search_filter),
                Investigation.batch_lot_number.ilike(search_filter),
                Investigation.title.ilike(search_filter),
            )
        )

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    investigations = result.scalars().all()

    # Build summary models
    summaries = []
    for inv in investigations:
        summaries.append(
            InvestigationSummaryResponse(
                id=inv.id,
                deviation_number=inv.deviation_number,
                title=inv.title,
                api_product_name=inv.api_product_name,
                batch_lot_number=inv.batch_lot_number,
                equipment_id=inv.equipment_id,
                manufacturing_stage=inv.manufacturing_stage,
                incident_date=inv.incident_date,
                severity=inv.severity,
                status=inv.status,
                source_type=inv.source_type,
                created_at=inv.created_at,
                updated_at=inv.updated_at,
                has_rca=len(inv.rca_analyses) > 0,
                capa_count=len(inv.capa_recommendations),
            )
        )
    return summaries


@router.post(
    "",
    response_model=InvestigationDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Save a reviewed RCA investigation with analyses and CAPAs in a single transaction",
)
async def create_investigation(
    payload: InvestigationCreateFull,
    db: AsyncSession = Depends(get_db),
):
    """
    Saves a reviewed RCA investigation along with its `rca_analyses` and `capa_recommendations`
    in a single atomic transaction.
    """
    # 1. Uniqueness check for deviation_number
    existing = await db.execute(
        select(Investigation).where(Investigation.deviation_number == payload.deviation_number)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Deviation number '{payload.deviation_number}' already exists.",
        )

    # 2. Extract investigation data
    inv_id = uuid.uuid4()
    inv_data = payload.model_dump(exclude={"rca_analysis", "rca_analyses", "capa_recommendations"})
    inv_data["id"] = inv_id
    investigation = Investigation(**inv_data)
    db.add(investigation)

    # 3. Add RCA analyses if provided in single transaction
    rca_items_to_add: List[RCAAnalysis] = []
    if isinstance(payload, InvestigationCreateFull):
        # Single rca_analysis
        if payload.rca_analysis:
            rca_obj = RCAAnalysis(
                id=uuid.uuid4(),
                investigation_id=inv_id,
                **payload.rca_analysis.model_dump(),
            )
            rca_items_to_add.append(rca_obj)
        # Multiple rca_analyses
        elif payload.rca_analyses:
            for rca_item in payload.rca_analyses:
                rca_obj = RCAAnalysis(
                    id=uuid.uuid4(),
                    investigation_id=inv_id,
                    **rca_item.model_dump(),
                )
                rca_items_to_add.append(rca_obj)

        for rca in rca_items_to_add:
            db.add(rca)

        # 4. Add CAPA recommendations if provided
        if payload.capa_recommendations:
            for capa_item in payload.capa_recommendations:
                capa_obj = CAPARecommendation(
                    id=uuid.uuid4(),
                    investigation_id=inv_id,
                    **capa_item.model_dump(),
                )
                db.add(capa_obj)

    # Commit atomic transaction
    await db.commit()

    # Re-query with eager loaded relationships
    result = await db.execute(
        select(Investigation)
        .options(
            selectinload(Investigation.rca_analyses),
            selectinload(Investigation.capa_recommendations),
        )
        .where(Investigation.id == inv_id)
    )
    saved_inv = result.scalar_one()
    return saved_inv


@router.get(
    "/{investigation_id}",
    response_model=InvestigationDetailResponse,
    summary="Get full investigation, RCA analysis, and CAPA list",
)
async def get_investigation(
    investigation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Returns the full investigation record with attached RCA analyses and CAPA list.
    """
    result = await db.execute(
        select(Investigation)
        .options(
            selectinload(Investigation.rca_analyses),
            selectinload(Investigation.capa_recommendations),
        )
        .where(Investigation.id == investigation_id)
    )
    investigation = result.scalar_one_or_none()
    if not investigation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Investigation with ID '{investigation_id}' not found.",
        )
    return investigation


@router.put(
    "/{investigation_id}",
    response_model=InvestigationDetailResponse,
    summary="Update existing investigation after user edits or QA confirmation",
)
async def update_investigation(
    investigation_id: uuid.UUID,
    payload: InvestigationUpdateFull,
    db: AsyncSession = Depends(get_db),
):
    """
    Updates an existing investigation after user edits or QA confirmation.
    Optionally replaces/updates nested RCA analyses and CAPA recommendations.
    """
    result = await db.execute(
        select(Investigation)
        .options(
            selectinload(Investigation.rca_analyses),
            selectinload(Investigation.capa_recommendations),
        )
        .where(Investigation.id == investigation_id)
    )
    investigation = result.scalar_one_or_none()
    if not investigation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Investigation with ID '{investigation_id}' not found.",
        )

    # Update top-level investigation fields
    update_data = payload.model_dump(
        exclude_unset=True,
        exclude={"rca_analysis", "rca_analyses", "capa_recommendations"},
    )
    for field, value in update_data.items():
        setattr(investigation, field, value)

    # If updating RCA / CAPA
    if isinstance(payload, InvestigationUpdateFull):
        # Update or add RCA analysis
        if payload.rca_analysis is not None:
            # Replace or update existing RCA
            await db.execute(
                delete(RCAAnalysis).where(RCAAnalysis.investigation_id == investigation_id)
            )
            new_rca = RCAAnalysis(
                id=uuid.uuid4(),
                investigation_id=investigation_id,
                **payload.rca_analysis.model_dump(),
            )
            db.add(new_rca)
        elif payload.rca_analyses is not None:
            await db.execute(
                delete(RCAAnalysis).where(RCAAnalysis.investigation_id == investigation_id)
            )
            for rca_item in payload.rca_analyses:
                new_rca = RCAAnalysis(
                    id=uuid.uuid4(),
                    investigation_id=investigation_id,
                    **rca_item.model_dump(),
                )
                db.add(new_rca)

        # Update or replace CAPA recommendations
        if payload.capa_recommendations is not None:
            await db.execute(
                delete(CAPARecommendation).where(CAPARecommendation.investigation_id == investigation_id)
            )
            for capa_item in payload.capa_recommendations:
                new_capa = CAPARecommendation(
                    id=uuid.uuid4(),
                    investigation_id=investigation_id,
                    **capa_item.model_dump(),
                )
                db.add(new_capa)

    await db.commit()

    # Re-fetch updated record with all relationships
    reloaded = await db.execute(
        select(Investigation)
        .options(
            selectinload(Investigation.rca_analyses),
            selectinload(Investigation.capa_recommendations),
        )
        .where(Investigation.id == investigation_id)
    )
    return reloaded.scalar_one()


@router.delete(
    "/{investigation_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete an investigation and its associated RCA/CAPA records",
)
async def delete_investigation(
    investigation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Deletes an investigation. Cascading deletion will automatically remove
    associated RCA analyses and CAPA recommendations.
    """
    result = await db.execute(
        select(Investigation).where(Investigation.id == investigation_id)
    )
    investigation = result.scalar_one_or_none()
    if not investigation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Investigation with ID '{investigation_id}' not found.",
        )

    await db.delete(investigation)
    await db.commit()
    return {
        "success": True,
        "message": f"Investigation '{investigation.deviation_number}' (ID: {investigation_id}) deleted successfully.",
        "id": str(investigation_id),
    }
