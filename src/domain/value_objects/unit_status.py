from enum import Enum
from typing import List


class UnitStatus(Enum):
    """Estados posibles de una unidad en el sistema de tracking"""
    
    CREATED = "CREATED"
    PICKED_UP = "PICKED_UP"
    IN_TRANSIT = "IN_TRANSIT"
    AT_FACILITY = "AT_FACILITY"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"
    EXCEPTION = "EXCEPTION"
    
    @classmethod
    def get_all_statuses(cls) -> List[str]:
        """Retorna todos los estados disponibles"""
        return [status.value for status in cls]
    
    @classmethod
    def is_valid_status(cls, status: str) -> bool:
        """Valida si un estado es válido"""
        try:
            cls(status)
            return True
        except ValueError:
            return False
    
    @classmethod
    def get_next_valid_statuses(cls, current_status: 'UnitStatus') -> List['UnitStatus']:
        """Retorna los estados válidos siguientes basado en el estado actual"""
        transitions = {
            cls.CREATED: [cls.PICKED_UP, cls.EXCEPTION],
            cls.PICKED_UP: [cls.IN_TRANSIT, cls.AT_FACILITY, cls.EXCEPTION],
            cls.IN_TRANSIT: [cls.AT_FACILITY, cls.OUT_FOR_DELIVERY, cls.EXCEPTION],
            cls.AT_FACILITY: [cls.OUT_FOR_DELIVERY, cls.IN_TRANSIT, cls.EXCEPTION],
            cls.OUT_FOR_DELIVERY: [cls.DELIVERED, cls.AT_FACILITY, cls.EXCEPTION],
            cls.DELIVERED: [],  # Estado final
            cls.EXCEPTION: [cls.PICKED_UP, cls.IN_TRANSIT, cls.AT_FACILITY]  # Puede recuperarse
        }
        return transitions.get(current_status, [])
    
    def can_transition_to(self, target_status: 'UnitStatus') -> bool:
        """Verifica si es posible hacer la transición al estado objetivo"""
        return target_status in self.get_next_valid_statuses(self)

