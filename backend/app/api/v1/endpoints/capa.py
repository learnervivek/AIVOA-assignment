import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.capa import CAPARecommendation
from app.schemas.capa import (
    CAPACreate,
    CAPAUpdate,
    CAPAResponse,
)

router = APIRouter()


@router.get("/by-investigation/{investigation_id}", response_model=List[CAPAResponse])
async def get_capa_by_investigation(
    investigation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve all CAPA recommendations for a deviation investigation."""
    result = await db.execute(
        select(CAPARecommendation)
        .where(CAPARecommendation.investigation_id == investigation_id)
        .order_by(CAPARecommendation.created_at.asc())
    )
    return result.scalars().all()


@router.post("", response_model=CAPAResponse, status_code=status.HTTP_201_CREATED)
async def create_capa(
    payload: CAPACreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new CAPA action item."""
    capa = CAPARecommendation(**payload.model_dump())
    db.add(capa)
    await db.commit()
    await db.refresh(capa)
    return capa


@router.patch("/{capa_id}", response_model=CAPAResponse)
async def update_capa(
    capa_id: uuid.UUID,
    payload: CAPAUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a CAPA recommendation status or ownership."""
    result = await db.execute(
        select(CAPARecommendation).where(CAPARecommendation.id == capa_id)
    )
    capa = result.scalar_one_or_none()
    if not capa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CAPA recommendation not found",
        )

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(capa, field, value)

    await db.commit()
    await db.refresh(capa)
    return capa
