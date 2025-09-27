from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities.checkpoint import Checkpoint
from ..value_objects.tracking_id import TrackingId


class CheckpointRepository(ABC):
    """Interfaz del repositorio para la entidad Checkpoint"""

    @abstractmethod
    def save(self, checkpoint: Checkpoint) -> Checkpoint:
        """Guarda un checkpoint en el repositorio"""
        pass

    @abstractmethod
    def find_by_tracking_id(self, tracking_id: TrackingId) -> List[Checkpoint]:
        """Busca todos los checkpoints de una unidad por tracking ID"""
        pass

    @abstractmethod
    def find_by_id(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """Busca un checkpoint por su ID"""
        pass

    @abstractmethod
    def find_latest_by_tracking_id(
        self, tracking_id: TrackingId
    ) -> Optional[Checkpoint]:
        """Busca el último checkpoint de una unidad"""
        pass

    @abstractmethod
    def find_all(self, limit: int = 100, offset: int = 0) -> List[Checkpoint]:
        """Retorna todos los checkpoints con paginación"""
        pass

    @abstractmethod
    def count_by_tracking_id(self, tracking_id: TrackingId) -> int:
        """Cuenta el número de checkpoints de una unidad"""
        pass

    @abstractmethod
    def delete(self, checkpoint_id: str) -> bool:
        """Elimina un checkpoint del repositorio"""
        pass
