import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.rca_analysis import RCAAnalysis
from app.schemas.rca_analysis import (
    RCAAnalysisCreate,
    RCAAnalysisUpdate,
    RCAAnalysisResponse,
)

router = APIRouter()


@router.get("/by-investigation/{investigation_id}", response_model=List[RCAAnalysisResponse])
async def get_rca_by_investigation(
    investigation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve all RCA analyses associated with a specific deviation investigation."""
    result = await db.execute(
        select(RCAAnalysis)
        .where(RCAAnalysis.investigation_id == investigation_id)
        .order_by(RCAAnalysis.created_at.desc())
    )
    return result.scalars().all()


@router.post("", response_model=RCAAnalysisResponse, status_code=status.HTTP_201_CREATED)
async def create_rca_analysis(
    payload: RCAAnalysisCreate,
    db: AsyncSession = Depends(get_db),
):
    """Save an RCA analysis record (5 Whys / 6M Ishikawa Fishbone)."""
    rca = RCAAnalysis(**payload.model_dump())
    db.add(rca)
    await db.commit()
    await db.refresh(rca)
    return rca


@router.patch("/{rca_id}", response_model=RCAAnalysisResponse)
async def update_rca_analysis(
    rca_id: uuid.UUID,
    payload: RCAAnalysisUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update RCA findings, root cause confirmations, or missing evidence."""
    result = await db.execute(select(RCAAnalysis).where(RCAAnalysis.id == rca_id))
    rca = result.scalar_one_or_none()
    if not rca:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RCA analysis record not found",
        )

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(rca, field, value)

    await db.commit()
    await db.refresh(rca)
    return rca
