from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from ..value_objects.tracking_id import TrackingId
from ..value_objects.unit_status import UnitStatus


@dataclass
class Shipment:
    """Entidad de dominio que representa un envío (guía) que puede contener múltiples unidades"""
    
    tracking_id: TrackingId
    units: List[str]  # Lista de IDs de unidades
    created_at: datetime
    updated_at: datetime
    id: Optional[str] = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid4())
    
    @classmethod
    def create(cls, tracking_id: TrackingId, unit_ids: List[str]) -> 'Shipment':
        """Factory method para crear un nuevo envío"""
        now = datetime.utcnow()
        return cls(
            tracking_id=tracking_id,
            units=unit_ids,
            created_at=now,
            updated_at=now
        )
    
    def add_unit(self, unit_id: str) -> None:
        """Agrega una unidad al envío"""
        if unit_id not in self.units:
            self.units.append(unit_id)
            self.updated_at = datetime.utcnow()
    
    def remove_unit(self, unit_id: str) -> None:
        """Remueve una unidad del envío"""
        if unit_id in self.units:
            self.units.remove(unit_id)
            self.updated_at = datetime.utcnow()
    
    def get_unit_count(self) -> int:
        """Retorna el número de unidades en el envío"""
        return len(self.units)
    
    def to_dict(self) -> dict:
        """Convierte el envío a diccionario"""
        return {
            'id': self.id,
            'tracking_id': str(self.tracking_id),
            'units': self.units,
            'unit_count': self.get_unit_count(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

