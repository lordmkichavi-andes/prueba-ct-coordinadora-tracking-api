from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities.shipment import Shipment
from ..value_objects.tracking_id import TrackingId


class ShipmentRepository(ABC):
    """Interfaz del repositorio para la entidad Shipment"""

    @abstractmethod
    def save(self, shipment: Shipment) -> Shipment:
        """Guarda un envío en el repositorio"""
        pass

    @abstractmethod
    def find_by_tracking_id(self, tracking_id: TrackingId) -> Optional[Shipment]:
        """Busca un envío por su tracking ID"""
        pass

    @abstractmethod
    def find_by_id(self, shipment_id: str) -> Optional[Shipment]:
        """Busca un envío por su ID"""
        pass

    @abstractmethod
    def find_all(self, limit: int = 100, offset: int = 0) -> List[Shipment]:
        """Retorna todos los envíos con paginación"""
        pass

    @abstractmethod
    def exists_by_tracking_id(self, tracking_id: TrackingId) -> bool:
        """Verifica si existe un envío con el tracking ID dado"""
        pass

    @abstractmethod
    def delete(self, shipment_id: str) -> bool:
        """Elimina un envío del repositorio"""
        pass
