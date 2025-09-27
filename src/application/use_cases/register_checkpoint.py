from typing import Optional
import structlog

from ...domain.entities.unit import Unit
from ...domain.entities.checkpoint import Checkpoint
from ...domain.value_objects.tracking_id import TrackingId
from ...domain.value_objects.checkpoint_data import CheckpointData
from ...domain.repositories.unit_repository import UnitRepository
from ...domain.repositories.checkpoint_repository import CheckpointRepository
from ...application.interfaces.unit_service import UnitService

logger = structlog.get_logger(__name__)


class RegisterCheckpointUseCase:
    """Caso de uso para registrar un checkpoint en una unidad"""
    
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
        checkpoint_data: CheckpointData
    ) -> dict:
        """
        Registra un checkpoint para una unidad
        
        Args:
            tracking_id: ID de tracking de la unidad
            checkpoint_data: Datos del checkpoint
            
        Returns:
            dict: Información del checkpoint registrado
            
        Raises:
            ValueError: Si la unidad no existe o la transición no es válida
        """
        logger.info(
            "Registrando checkpoint",
            tracking_id=str(tracking_id),
            status=checkpoint_data.status.value
        )
        
        # Verificar que la unidad existe, si no existe, crearla
        unit = self.unit_repository.find_by_tracking_id(tracking_id)
        if not unit:
            logger.info(
                "Unidad no encontrada, creando nueva unidad",
                tracking_id=str(tracking_id)
            )
            # Crear nueva unidad con estado inicial
            from src.domain.entities.unit import Unit
            from src.domain.value_objects.unit_status import UnitStatus
            from datetime import datetime
            
            # Crear unidad con estado inicial CREATED si el checkpoint no es CREATED
            initial_status = UnitStatus.CREATED if checkpoint_data.status != UnitStatus.CREATED else checkpoint_data.status
            unit = Unit(
                id=None,  # Se generará automáticamente
                tracking_id=tracking_id,
                current_status=initial_status,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                checkpoints=[]  # Lista vacía inicialmente
            )
            unit = self.unit_repository.save(unit)
        
        # Agregar checkpoint a la unidad
        try:
            updated_unit = self.unit_service.add_checkpoint(tracking_id, checkpoint_data)
        except ValueError as e:
            logger.error(
                "Error al agregar checkpoint",
                tracking_id=str(tracking_id),
                error=str(e)
            )
            raise
        
        # Crear checkpoint inmutable
        checkpoint = Checkpoint.create(tracking_id, checkpoint_data)
        
        # Guardar en repositorios
        saved_unit = self.unit_repository.save(updated_unit)
        saved_checkpoint = self.checkpoint_repository.save(checkpoint)
        
        logger.info(
            "Checkpoint registrado exitosamente",
            tracking_id=str(tracking_id),
            checkpoint_id=saved_checkpoint.id,
            new_status=checkpoint_data.status.value
        )
        
        return {
            'checkpoint': saved_checkpoint.to_dict(),
            'unit': saved_unit.to_dict()
        }
