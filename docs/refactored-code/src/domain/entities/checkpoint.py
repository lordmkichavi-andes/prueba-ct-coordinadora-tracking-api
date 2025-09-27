from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import uuid4

from ..value_objects.checkpoint_data import CheckpointData
from ..value_objects.tracking_id import TrackingId


@dataclass
class Checkpoint:
    """Entidad de dominio que representa un checkpoint inmutable"""

    tracking_id: TrackingId
    checkpoint_data: CheckpointData
    created_at: datetime
    id: Optional[str] = None

    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid4())

    @classmethod
    def create(
        cls, tracking_id: TrackingId, checkpoint_data: CheckpointData
    ) -> "Checkpoint":
        """Factory method para crear un nuevo checkpoint"""
        return cls(
            tracking_id=tracking_id,
            checkpoint_data=checkpoint_data,
            created_at=datetime.utcnow(),
        )

    def to_dict(self) -> dict:
        """Convierte el checkpoint a diccionario"""
        return {
            "id": self.id,
            "tracking_id": str(self.tracking_id),
            "created_at": self.created_at.isoformat(),
            **self.checkpoint_data.to_dict(),
        }
