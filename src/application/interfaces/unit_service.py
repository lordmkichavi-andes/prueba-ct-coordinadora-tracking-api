from abc import ABC, abstractmethod
from typing import List, Optional

from ...domain.entities.unit import Unit
from ...domain.value_objects.tracking_id import TrackingId
from ...domain.value_objects.unit_status import UnitStatus
from ...domain.value_objects.checkpoint_data import CheckpointData


class UnitService(ABC):
    """Interfaz del servicio de dominio para Unit"""
    
    @abstractmethod
    def create_unit(self, tracking_id: TrackingId) -> Unit:
        """Crea una nueva unidad"""
        pass
    
    @abstractmethod
    def add_checkpoint(self, tracking_id: TrackingId, checkpoint_data: CheckpointData) -> Unit:
        """Agrega un checkpoint a una unidad existente"""
        pass
    
    @abstractmethod
    def get_unit_by_tracking_id(self, tracking_id: TrackingId) -> Optional[Unit]:
        """Obtiene una unidad por su tracking ID"""
        pass
    
    @abstractmethod
    def get_units_by_status(self, status: UnitStatus) -> List[Unit]:
        """Obtiene todas las unidades con un estado específico"""
        pass
    
    @abstractmethod
    def get_unit_tracking_history(self, tracking_id: TrackingId) -> List[CheckpointData]:
        """Obtiene el historial de tracking de una unidad"""
        pass

