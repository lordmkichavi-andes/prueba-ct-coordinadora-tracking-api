from typing import List, Optional

import structlog

from ...domain.entities.unit import Unit
from ...domain.repositories.checkpoint_repository import CheckpointRepository
from ...domain.repositories.unit_repository import UnitRepository
from ...domain.value_objects.tracking_id import TrackingId

logger = structlog.get_logger(__name__)


class GetTrackingHistoryUseCase:
    """Caso de uso para obtener el historial de tracking de una unidad"""

    def __init__(
        self,
        unit_repository: UnitRepository,
        checkpoint_repository: CheckpointRepository,
    ):
        self.unit_repository = unit_repository
        self.checkpoint_repository = checkpoint_repository

    def execute(self, tracking_id: TrackingId) -> dict:
        """
        Obtiene el historial completo de tracking de una unidad

        Args:
            tracking_id: ID de tracking de la unidad

        Returns:
            dict: Información de la unidad y su historial de checkpoints

        Raises:
            ValueError: Si la unidad no existe
        """
        logger.info("Obteniendo historial de tracking", tracking_id=str(tracking_id))

        # Buscar la unidad
        unit = self.unit_repository.find_by_tracking_id(tracking_id)
        if not unit:
            logger.warning(
                "Unidad no encontrada para historial", tracking_id=str(tracking_id)
            )
            raise ValueError(f"Unidad con tracking ID {tracking_id} no encontrada")

        # Obtener todos los checkpoints de la unidad
        checkpoints = self.checkpoint_repository.find_by_tracking_id(tracking_id)

        # Ordenar checkpoints por timestamp
        checkpoints.sort(key=lambda cp: cp.checkpoint_data.timestamp)

        logger.info(
            "Historial obtenido exitosamente",
            tracking_id=str(tracking_id),
            checkpoint_count=len(checkpoints),
        )

        return {
            "unit": unit.to_dict(),
            "checkpoints": [cp.to_dict() for cp in checkpoints],
            "total_checkpoints": len(checkpoints),
        }
