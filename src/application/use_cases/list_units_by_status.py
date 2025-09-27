from typing import List
import structlog

from ...domain.entities.unit import Unit
from ...domain.value_objects.unit_status import UnitStatus
from ...domain.repositories.unit_repository import UnitRepository

logger = structlog.get_logger(__name__)


class ListUnitsByStatusUseCase:
    """Caso de uso para listar unidades por estado"""
    
    def __init__(self, unit_repository: UnitRepository):
        self.unit_repository = unit_repository
    
    def execute(
        self,
        status: UnitStatus,
        limit: int = 100,
        offset: int = 0
    ) -> dict:
        """
        Lista unidades filtradas por estado
        
        Args:
            status: Estado de las unidades a buscar
            limit: Límite de resultados
            offset: Offset para paginación
            
        Returns:
            dict: Lista de unidades y metadatos de paginación
        """
        logger.info(
            "Listando unidades por estado",
            status=status.value,
            limit=limit,
            offset=offset
        )
        
        # Validar parámetros
        if limit <= 0 or limit > 1000:
            limit = 100
        
        if offset < 0:
            offset = 0
        
        # Buscar unidades por estado
        units = self.unit_repository.find_by_status(status)
        
        # Aplicar paginación
        total_count = len(units)
        paginated_units = units[offset:offset + limit]
        
        logger.info(
            "Unidades listadas exitosamente",
            status=status.value,
            total_count=total_count,
            returned_count=len(paginated_units)
        )
        
        return {
            'units': [unit.to_dict() for unit in paginated_units],
            'pagination': {
                'total': total_count,
                'limit': limit,
                'offset': offset,
                'has_more': offset + limit < total_count
            },
            'status': status.value
        }

