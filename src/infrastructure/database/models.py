import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .database import db


class UnitModel(db.Model):
    """Modelo SQLAlchemy para la entidad Unit"""

    __tablename__ = "units"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tracking_id = Column(String(50), unique=True, nullable=False, index=True)
    current_status = Column(String(20), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relación con checkpoints
    checkpoints = relationship(
        "CheckpointModel", back_populates="unit", cascade="all, delete-orphan"
    )


class CheckpointModel(db.Model):
    """Modelo SQLAlchemy para la entidad Checkpoint"""

    __tablename__ = "checkpoints"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tracking_id = Column(String(50), nullable=False, index=True)
    status = Column(String(20), nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    location = Column(String(200), nullable=True)
    notes = Column(Text, nullable=True)
    operator_id = Column(String(50), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relación con unidad
    unit_id = Column(String(36), ForeignKey("units.id"), nullable=True)
    unit = relationship("UnitModel", back_populates="checkpoints")


class ShipmentModel(db.Model):
    """Modelo SQLAlchemy para la entidad Shipment"""

    __tablename__ = "shipments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tracking_id = Column(String(50), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relación con unidades (many-to-many a través de tabla intermedia)
    units = relationship(
        "ShipmentUnitModel", back_populates="shipment", cascade="all, delete-orphan"
    )


class ShipmentUnitModel(db.Model):
    """Modelo intermedio para la relación many-to-many entre Shipment y Unit"""

    __tablename__ = "shipment_units"

    id = Column(Integer, primary_key=True, autoincrement=True)
    shipment_id = Column(String(36), ForeignKey("shipments.id"), nullable=False)
    unit_id = Column(String(36), ForeignKey("units.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relaciones
    shipment = relationship("ShipmentModel", back_populates="units")
    unit = relationship("UnitModel")
