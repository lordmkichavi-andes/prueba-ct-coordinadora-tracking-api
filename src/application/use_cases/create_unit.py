from typing import Optional
import structlog

from ...domain.entities.unit import Unit
from ...domain.value_objects.tracking_id import TrackingId
from ...domain.value_objects.unit_status import UnitStatus
from ...domain.repositories.unit_repository import UnitRepository
from ...domain.repositories.checkpoint_repository import CheckpointRepository
from ...application.interfaces.unit_service import UnitService

logger = structlog.get_logger(__name__)


class CreateUnitUseCase:
    """Caso de uso para crear una nueva unidad"""
    
    def __init__(
        self,
        unit_repository: UnitRepository,
        checkpoint_repository: CheckpointRepository,
        unit_service: UnitService
    ):
        self.unit_repository = unit_repository
        self.checkpoint_repository = checkpoint_repository
        self.unit_service = unit_service
    
    def execute(
        self,
        tracking_id: TrackingId,
        initial_status: UnitStatus = UnitStatus.CREATED
    ) -> dict:
        """
        Crea una nueva unidad
        
        Args:
            tracking_id: ID de tracking de la unidad
            initial_status: Estado inicial de la unidad
            
        Returns:
            dict: Información de la unidad creada
            
        Raises:
            ValueError: Si la unidad ya existe
        """
        logger.info(
            "Creando nueva unidad",
            tracking_id=str(tracking_id),
            initial_status=initial_status.value
        )
        
        # Verificar que la unidad no existe
        existing_unit = self.unit_repository.find_by_tracking_id(tracking_id)
        if existing_unit:
            logger.warning(
                "Unidad ya existe",
                tracking_id=str(tracking_id)
            )
            raise ValueError(f"Unidad con tracking ID {tracking_id} ya existe")
        
        # Crear la unidad
        unit = self.unit_service.create_unit(tracking_id)
        
        # Guardar en repositorio
        saved_unit = self.unit_repository.save(unit)
        
        # Crear checkpoint inicial
        from ...domain.value_objects.checkpoint_data import CheckpointData
        from ...domain.entities.checkpoint import Checkpoint
        
        initial_checkpoint_data = CheckpointData(
            status=initial_status,
            timestamp=unit.created_at
        )
        initial_checkpoint = Checkpoint.create(tracking_id, initial_checkpoint_data)
        saved_checkpoint = self.checkpoint_repository.save(initial_checkpoint)
        
        logger.info(
            "Unidad creada exitosamente",
            tracking_id=str(tracking_id),
            unit_id=saved_unit.id,
            checkpoint_id=saved_checkpoint.id
        )
        
        return {
            'unit': saved_unit.to_dict(),
            'initial_checkpoint': saved_checkpoint.to_dict()
        }

