import re
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class TrackingId:
    """Value Object para el ID de tracking de una unidad"""

    value: str

    def __post_init__(self):
        if not self.value:
            raise ValueError("Tracking ID no puede estar vacío")

        if len(self.value) < 3:
            raise ValueError("Tracking ID debe tener al menos 3 caracteres")

        if len(self.value) > 50:
            raise ValueError("Tracking ID no puede exceder 50 caracteres")

        # Validar formato alfanumérico
        if not re.match(r"^[A-Za-z0-9\-_]+$", self.value):
            raise ValueError(
                "Tracking ID solo puede contener letras, números, guiones y guiones bajos"
            )

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other) -> bool:
        if not isinstance(other, TrackingId):
            return False
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)
