import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    String,
    Text,
    DateTime,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Investigation(Base):
    __tablename__ = "investigations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    deviation_number: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    api_product_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    batch_lot_number: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    equipment_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    manufacturing_stage: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )
    incident_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    severity: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="Major",  # Critical, Major, Minor
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    immediate_containment: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    raw_input_text: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    source_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="text",  # pdf, email, text
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="Draft",  # Draft, Under Review, QA Approved
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    rca_analyses: Mapped[List["RCAAnalysis"]] = relationship(
        "RCAAnalysis",
        back_populates="investigation",
        cascade="all, delete-orphan",
        order_by="desc(RCAAnalysis.created_at)",
    )
    capa_recommendations: Mapped[List["CAPARecommendation"]] = relationship(
        "CAPARecommendation",
        back_populates="investigation",
        cascade="all, delete-orphan",
        order_by="desc(CAPARecommendation.created_at)",
    )
