from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .unit_status import UnitStatus


@dataclass(frozen=True)
class CheckpointData:
    """Value Object que contiene los datos de un checkpoint"""

    status: UnitStatus
    timestamp: datetime
    location: Optional[str] = None
    notes: Optional[str] = None
    operator_id: Optional[str] = None

    def __post_init__(self):
        if not isinstance(self.status, UnitStatus):
            raise ValueError("Status debe ser una instancia de UnitStatus")

        if not isinstance(self.timestamp, datetime):
            raise ValueError("Timestamp debe ser una instancia de datetime")

        # Validar que el timestamp no sea futuro
        now = datetime.utcnow()
        if self.timestamp.tzinfo is not None:
            # Si tiene timezone, convertir a UTC naive para comparar
            now = now.replace(tzinfo=None)
        if self.timestamp > now:
            raise ValueError("Timestamp no puede ser futuro")

        # Validar longitud de campos opcionales
        if self.location and len(self.location) > 200:
            raise ValueError("Location no puede exceder 200 caracteres")

        if self.notes and len(self.notes) > 500:
            raise ValueError("Notes no puede exceder 500 caracteres")

        if self.operator_id and len(self.operator_id) > 50:
            raise ValueError("Operator ID no puede exceder 50 caracteres")

    def to_dict(self) -> dict:
        """Convierte el checkpoint a diccionario"""
        return {
            "status": self.status.value,
            "timestamp": self.timestamp.isoformat(),
            "location": self.location,
            "notes": self.notes,
            "operator_id": self.operator_id,
        }
