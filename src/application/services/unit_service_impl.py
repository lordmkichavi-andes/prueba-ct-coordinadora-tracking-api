from typing import List, Optional
import structlog

from ...domain.entities.unit import Unit
from ...domain.value_objects.tracking_id import TrackingId
from ...domain.value_objects.unit_status import UnitStatus
from ...domain.value_objects.checkpoint_data import CheckpointData
from ...domain.repositories.unit_repository import UnitRepository
from ...application.interfaces.unit_service import UnitService

logger = structlog.get_logger(__name__)


class UnitServiceImpl(UnitService):
    """Implementación del servicio de dominio para Unit"""
    
    def __init__(self, unit_repository: UnitRepository):
        self.unit_repository = unit_repository
    
    def create_unit(self, tracking_id: TrackingId) -> Unit:
        """Crea una nueva unidad"""
        logger.info(
            "Creando nueva unidad",
            tracking_id=str(tracking_id)
        )
        
        # Verificar que la unidad no existe
        existing_unit = self.unit_repository.find_by_tracking_id(tracking_id)
        if existing_unit:
            raise ValueError(f"Unidad con tracking ID {tracking_id} ya existe")
        
        # Crear la unidad
        unit = Unit.create(tracking_id, UnitStatus.CREATED)
        
        logger.info(
            "Unidad creada exitosamente",
            tracking_id=str(tracking_id),
            unit_id=unit.id
        )
        
        return unit
    
    def add_checkpoint(self, tracking_id: TrackingId, checkpoint_data: CheckpointData) -> Unit:
        """Agrega un checkpoint a una unidad existente"""
        logger.info(
            "Agregando checkpoint a unidad",
            tracking_id=str(tracking_id),
            status=checkpoint_data.status.value
        )
        
        # Buscar la unidad
        unit = self.unit_repository.find_by_tracking_id(tracking_id)
        if not unit:
            raise ValueError(f"Unidad con tracking ID {tracking_id} no encontrada")
        
        # Agregar checkpoint
        unit.add_checkpoint(checkpoint_data)
        
        logger.info(
            "Checkpoint agregado exitosamente",
            tracking_id=str(tracking_id),
            new_status=checkpoint_data.status.value
        )
        
        return unit
    
    def get_unit_by_tracking_id(self, tracking_id: TrackingId) -> Optional[Unit]:
        """Obtiene una unidad por su tracking ID"""
        return self.unit_repository.find_by_tracking_id(tracking_id)
    
    def get_units_by_status(self, status: UnitStatus) -> List[Unit]:
        """Obtiene todas las unidades con un estado específico"""
        return self.unit_repository.find_by_status(status)
    
    def get_unit_tracking_history(self, tracking_id: TrackingId) -> List[CheckpointData]:
        """Obtiene el historial de tracking de una unidad"""
        unit = self.unit_repository.find_by_tracking_id(tracking_id)
        if not unit:
            raise ValueError(f"Unidad con tracking ID {tracking_id} no encontrada")
        
        return unit.get_checkpoint_history()

