from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from ..value_objects.tracking_id import TrackingId
from ..value_objects.unit_status import UnitStatus
from ..value_objects.checkpoint_data import CheckpointData


@dataclass
class Unit:
    """Entidad de dominio que representa una unidad de envío"""
    
    tracking_id: TrackingId
    current_status: UnitStatus
    created_at: datetime
    updated_at: datetime
    checkpoints: List[CheckpointData]
    id: Optional[str] = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid4())
        
        if not self.checkpoints:
            self.checkpoints = []
    
    @classmethod
    def create(cls, tracking_id: TrackingId, initial_status: UnitStatus = UnitStatus.CREATED) -> 'Unit':
        """Factory method para crear una nueva unidad"""
        now = datetime.utcnow()
        initial_checkpoint = CheckpointData(
            status=initial_status,
            timestamp=now
        )
        
        return cls(
            tracking_id=tracking_id,
            current_status=initial_status,
            created_at=now,
            updated_at=now,
            checkpoints=[initial_checkpoint]
        )
    
    def add_checkpoint(self, checkpoint_data: CheckpointData) -> None:
        """Agrega un nuevo checkpoint a la unidad"""
        # Validar transición de estado
        if not self.current_status.can_transition_to(checkpoint_data.status):
            raise ValueError(
                f"No se puede cambiar de {self.current_status.value} a {checkpoint_data.status.value}"
            )
        
        # Validar que el timestamp sea posterior al último checkpoint
        if self.checkpoints and checkpoint_data.timestamp <= self.checkpoints[-1].timestamp:
            raise ValueError("El timestamp del nuevo checkpoint debe ser posterior al último")
        
        self.checkpoints.append(checkpoint_data)
        self.current_status = checkpoint_data.status
        self.updated_at = datetime.utcnow()
    
    def get_checkpoint_history(self) -> List[CheckpointData]:
        """Retorna el historial completo de checkpoints"""
        return self.checkpoints.copy()
    
    def get_last_checkpoint(self) -> Optional[CheckpointData]:
        """Retorna el último checkpoint"""
        return self.checkpoints[-1] if self.checkpoints else None
    
    def is_delivered(self) -> bool:
        """Verifica si la unidad ha sido entregada"""
        return self.current_status == UnitStatus.DELIVERED
    
    def has_exception(self) -> bool:
        """Verifica si la unidad tiene una excepción"""
        return self.current_status == UnitStatus.EXCEPTION
    
    def get_delivery_time(self) -> Optional[datetime]:
        """Retorna el timestamp de entrega si está disponible"""
        for checkpoint in reversed(self.checkpoints):
            if checkpoint.status == UnitStatus.DELIVERED:
                return checkpoint.timestamp
        return None
    
    def to_dict(self) -> dict:
        """Convierte la unidad a diccionario"""
        return {
            'id': self.id,
            'tracking_id': str(self.tracking_id),
            'current_status': self.current_status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'checkpoints': [cp.to_dict() for cp in self.checkpoints],
            'is_delivered': self.is_delivered(),
            'has_exception': self.has_exception(),
            'delivery_time': self.get_delivery_time().isoformat() if self.get_delivery_time() and hasattr(self.get_delivery_time(), 'isoformat') else None
        }
