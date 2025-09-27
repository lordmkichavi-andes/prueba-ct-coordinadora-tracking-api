from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities.unit import Unit
from ..value_objects.tracking_id import TrackingId
from ..value_objects.unit_status import UnitStatus


class UnitRepository(ABC):
    """Interfaz del repositorio para la entidad Unit"""

    @abstractmethod
    def save(self, unit: Unit) -> Unit:
        """Guarda una unidad en el repositorio"""
        pass

    @abstractmethod
    def find_by_tracking_id(self, tracking_id: TrackingId) -> Optional[Unit]:
        """Busca una unidad por su tracking ID"""
        pass

    @abstractmethod
    def find_by_id(self, unit_id: str) -> Optional[Unit]:
        """Busca una unidad por su ID"""
        pass

    @abstractmethod
    def find_by_status(self, status: UnitStatus) -> List[Unit]:
        """Busca todas las unidades con un estado específico"""
        pass

    @abstractmethod
    def find_all(self, limit: int = 100, offset: int = 0) -> List[Unit]:
        """Retorna todas las unidades con paginación"""
        pass

    @abstractmethod
    def exists_by_tracking_id(self, tracking_id: TrackingId) -> bool:
        """Verifica si existe una unidad con el tracking ID dado"""
        pass

    @abstractmethod
    def count_by_status(self, status: UnitStatus) -> int:
        """Cuenta el número de unidades con un estado específico"""
        pass

    @abstractmethod
    def delete(self, unit_id: str) -> bool:
        """Elimina una unidad del repositorio"""
        pass
