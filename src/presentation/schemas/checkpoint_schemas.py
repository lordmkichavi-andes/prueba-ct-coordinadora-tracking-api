from datetime import datetime
from typing import Optional

from marshmallow import (Schema, ValidationError, fields, validate,
                         validates_schema)

from ...domain.value_objects.unit_status import UnitStatus


class CheckpointDataSchema(Schema):
    """Schema para validar datos de checkpoint"""

    status = fields.Str(
        required=True,
        validate=validate.OneOf(UnitStatus.get_all_statuses()),
        error_messages={"required": "Status es requerido"},
    )

    timestamp = fields.DateTime(
        required=False,
        missing=lambda: datetime.utcnow(),
        error_messages={"invalid": "Timestamp debe ser una fecha válida"},
    )

    location = fields.Str(
        required=False,
        allow_none=True,
        validate=validate.Length(max=200),
        error_messages={"invalid": "Location no puede exceder 200 caracteres"},
    )

    notes = fields.Str(
        required=False,
        allow_none=True,
        validate=validate.Length(max=500),
        error_messages={"invalid": "Notes no puede exceder 500 caracteres"},
    )

    operator_id = fields.Str(
        required=False,
        allow_none=True,
        validate=validate.Length(max=50),
        error_messages={"invalid": "Operator ID no puede exceder 50 caracteres"},
    )

    @validates_schema
    def validate_timestamp(self, data, **kwargs):
        """Valida que el timestamp no sea futuro"""
        timestamp = data.get("timestamp")
        if timestamp:
            # Convertir a UTC si no tiene timezone
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=None)
            now = datetime.utcnow()
            if timestamp > now:
                raise ValidationError("Timestamp no puede ser futuro", "timestamp")


class RegisterCheckpointSchema(Schema):
    """Schema para registrar un checkpoint"""

    tracking_id = fields.Str(
        required=True,
        validate=[
            validate.Length(min=3, max=50),
            validate.Regexp(
                r"^[A-Za-z0-9\-_]+$",
                error="Solo se permiten letras, números, guiones y guiones bajos",
            ),
        ],
        error_messages={"required": "Tracking ID es requerido"},
    )

    checkpoint_data = fields.Nested(
        CheckpointDataSchema,
        required=True,
        error_messages={"required": "Checkpoint data es requerido"},
    )


class CheckpointResponseSchema(Schema):
    """Schema para respuesta de checkpoint"""

    id = fields.Str()
    tracking_id = fields.Str()
    status = fields.Str()
    timestamp = fields.Str()
    location = fields.Str(allow_none=True)
    notes = fields.Str(allow_none=True)
    operator_id = fields.Str(allow_none=True)
    created_at = fields.Str()


class UnitResponseSchema(Schema):
    """Schema para respuesta de unidad"""

    id = fields.Str()
    tracking_id = fields.Str()
    current_status = fields.Str()
    created_at = fields.Str()
    updated_at = fields.Str()
    is_delivered = fields.Bool()
    has_exception = fields.Bool()
    delivery_time = fields.Str(allow_none=True)


class RegisterCheckpointResponseSchema(Schema):
    """Schema para respuesta de registro de checkpoint"""

    checkpoint = fields.Nested(CheckpointResponseSchema)
    unit = fields.Nested(UnitResponseSchema)


class TrackingHistoryResponseSchema(Schema):
    """Schema para respuesta de historial de tracking"""

    unit = fields.Nested(UnitResponseSchema)
    checkpoints = fields.List(fields.Nested(CheckpointResponseSchema))
    total_checkpoints = fields.Int()


class ListUnitsByStatusSchema(Schema):
    """Schema para listar unidades por estado"""

    status = fields.Str(
        required=True,
        validate=validate.OneOf(UnitStatus.get_all_statuses()),
        error_messages={"required": "Status es requerido"},
    )

    limit = fields.Int(
        required=False,
        missing=100,
        validate=validate.Range(min=1, max=1000),
        error_messages={"invalid": "Limit debe estar entre 1 y 1000"},
    )

    offset = fields.Int(
        required=False,
        missing=0,
        validate=validate.Range(min=0),
        error_messages={"invalid": "Offset debe ser mayor o igual a 0"},
    )


class PaginationSchema(Schema):
    """Schema para información de paginación"""

    total = fields.Int()
    limit = fields.Int()
    offset = fields.Int()
    has_more = fields.Bool()


class ListUnitsResponseSchema(Schema):
    """Schema para respuesta de lista de unidades"""

    units = fields.List(fields.Nested(UnitResponseSchema))
    pagination = fields.Nested(PaginationSchema)
    status = fields.Str()


class ErrorResponseSchema(Schema):
    """Schema para respuestas de error"""

    error = fields.Str()
    message = fields.Str()
    details = fields.Dict(allow_none=True)
