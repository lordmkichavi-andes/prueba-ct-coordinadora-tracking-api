from flask import request, jsonify
from marshmallow import ValidationError
import structlog

from ...domain.value_objects.tracking_id import TrackingId
from ...domain.value_objects.unit_status import UnitStatus
from ...domain.value_objects.checkpoint_data import CheckpointData
from ...application.use_cases.register_checkpoint import RegisterCheckpointUseCase
from ...application.use_cases.get_tracking_history import GetTrackingHistoryUseCase
from ...application.use_cases.list_units_by_status import ListUnitsByStatusUseCase
# Las tareas de Celery se importan dinámicamente para evitar problemas de contexto
from ..schemas.checkpoint_schemas import (
    RegisterCheckpointSchema,
    RegisterCheckpointResponseSchema,
    TrackingHistoryResponseSchema,
    ListUnitsByStatusSchema,
    ListUnitsResponseSchema,
    ErrorResponseSchema
)

logger = structlog.get_logger(__name__)


class CheckpointController:
    """Controlador para endpoints de checkpoints"""
    
    def __init__(
        self,
        register_checkpoint_use_case: RegisterCheckpointUseCase,
        get_tracking_history_use_case: GetTrackingHistoryUseCase,
        list_units_by_status_use_case: ListUnitsByStatusUseCase
    ):
        self.register_checkpoint_use_case = register_checkpoint_use_case
        self.get_tracking_history_use_case = get_tracking_history_use_case
        self.list_units_by_status_use_case = list_units_by_status_use_case
    
    def register_checkpoint(self):
        """POST /api/v1/checkpoints - Registrar checkpoint"""
        try:
            # Validar datos de entrada
            schema = RegisterCheckpointSchema()
            data = schema.load(request.json)
            
            # Crear objetos de dominio
            tracking_id = TrackingId(data['tracking_id'])
            checkpoint_data = CheckpointData(
                status=UnitStatus(data['checkpoint_data']['status']),
                timestamp=data['checkpoint_data']['timestamp'],
                location=data['checkpoint_data'].get('location'),
                notes=data['checkpoint_data'].get('notes'),
                operator_id=data['checkpoint_data'].get('operator_id')
            )
            
            # Ejecutar caso de uso
            result = self.register_checkpoint_use_case.execute(tracking_id, checkpoint_data)
            
            # Ejecutar tareas asíncronas
            try:
                # Importar tareas dinámicamente para evitar problemas de contexto
                from ...infrastructure.external.tasks import process_checkpoint, send_notification
                
                # Procesar checkpoint de forma asíncrona
                process_task = process_checkpoint.delay(
                    str(tracking_id),
                    {
                        'status': checkpoint_data.status.value,
                        'timestamp': checkpoint_data.timestamp.isoformat() if checkpoint_data.timestamp else None,
                        'location': checkpoint_data.location,
                        'notes': checkpoint_data.notes,
                        'operator_id': checkpoint_data.operator_id
                    }
                )
                
                # Enviar notificación si es un estado importante
                if checkpoint_data.status in [UnitStatus.DELIVERED, UnitStatus.EXCEPTION]:
                    notification_task = send_notification.delay(
                        str(tracking_id),
                        checkpoint_data.status.value,
                        'customer@example.com'  # En producción esto vendría de la base de datos
                    )
                    logger.info(
                        "Tareas asíncronas iniciadas",
                        tracking_id=str(tracking_id),
                        process_task_id=process_task.id,
                        notification_task_id=notification_task.id
                    )
                else:
                    logger.info(
                        "Tarea de procesamiento iniciada",
                        tracking_id=str(tracking_id),
                        process_task_id=process_task.id
                    )
                    
            except Exception as e:
                # No fallar la respuesta principal si las tareas asíncronas fallan
                logger.error(
                    "Error iniciando tareas asíncronas",
                    tracking_id=str(tracking_id),
                    error=str(e),
                    error_type=str(type(e)),
                    error_args=str(e.args) if hasattr(e, 'args') else None
                )
            
            # Preparar respuesta
            response_schema = RegisterCheckpointResponseSchema()
            response_data = response_schema.dump(result)
            
            logger.info(
                "Checkpoint registrado exitosamente",
                tracking_id=str(tracking_id),
                status=checkpoint_data.status.value
            )
            
            return jsonify(response_data), 201
            
        except ValidationError as e:
            logger.warning(
                "Error de validación en registro de checkpoint",
                errors=e.messages
            )
            return jsonify({
                'error': 'validation_error',
                'message': 'Datos de entrada inválidos',
                'details': e.messages
            }), 400
            
        except ValueError as e:
            logger.warning(
                "Error de negocio en registro de checkpoint",
                error=str(e)
            )
            return jsonify({
                'error': 'business_error',
                'message': str(e)
            }), 400
            
        except Exception as e:
            logger.error(
                "Error interno en registro de checkpoint",
                error=str(e)
            )
            return jsonify({
                'error': 'internal_error',
                'message': 'Error interno del servidor'
            }), 500
    
    def get_tracking_history(self, tracking_id: str):
        """GET /api/v1/tracking/:trackingId - Obtener historial"""
        try:
            # Validar tracking ID
            try:
                tracking_id_obj = TrackingId(tracking_id)
            except ValueError as e:
                return jsonify({
                    'error': 'validation_error',
                    'message': str(e)
                }), 400
            
            # Ejecutar caso de uso
            result = self.get_tracking_history_use_case.execute(tracking_id_obj)
            
            # Preparar respuesta
            response_schema = TrackingHistoryResponseSchema()
            response_data = response_schema.dump(result)
            
            logger.info(
                "Historial obtenido exitosamente",
                tracking_id=tracking_id
            )
            
            return jsonify(response_data), 200
            
        except ValueError as e:
            logger.warning(
                "Error de negocio al obtener historial",
                tracking_id=tracking_id,
                error=str(e)
            )
            return jsonify({
                'error': 'business_error',
                'message': str(e)
            }), 404
            
        except Exception as e:
            logger.error(
                "Error interno al obtener historial",
                tracking_id=tracking_id,
                error=str(e)
            )
            return jsonify({
                'error': 'internal_error',
                'message': 'Error interno del servidor'
            }), 500
    
    def list_units_by_status(self):
        """GET /api/v1/shipments - Listar unidades por estado"""
        try:
            # Validar parámetros de consulta
            schema = ListUnitsByStatusSchema()
            data = schema.load(request.args)
            
            # Ejecutar caso de uso
            result = self.list_units_by_status_use_case.execute(
                status=UnitStatus(data['status']),
                limit=data['limit'],
                offset=data['offset']
            )
            
            # Preparar respuesta
            response_schema = ListUnitsResponseSchema()
            response_data = response_schema.dump(result)
            
            logger.info(
                "Unidades listadas exitosamente",
                status=data['status'],
                count=len(result['units'])
            )
            
            return jsonify(response_data), 200
            
        except ValidationError as e:
            logger.warning(
                "Error de validación al listar unidades",
                errors=e.messages
            )
            return jsonify({
                'error': 'validation_error',
                'message': 'Parámetros de consulta inválidos',
                'details': e.messages
            }), 400
            
        except Exception as e:
            logger.error(
                "Error interno al listar unidades",
                error=str(e)
            )
            return jsonify({
                'error': 'internal_error',
                'message': 'Error interno del servidor'
            }), 500
