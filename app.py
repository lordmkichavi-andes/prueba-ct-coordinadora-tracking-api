import os

import structlog
from flask import Flask, jsonify
from flask_cors import CORS

from src.application.services.unit_service_impl import UnitServiceImpl
from src.application.use_cases.get_tracking_history import \
    GetTrackingHistoryUseCase
from src.application.use_cases.list_units_by_status import \
    ListUnitsByStatusUseCase
from src.application.use_cases.register_checkpoint import \
    RegisterCheckpointUseCase
from src.domain.value_objects.unit_status import UnitStatus
from src.infrastructure.database.database import init_database
from src.infrastructure.external.celery_config import celery
from src.infrastructure.monitoring.health import create_health_endpoints
from src.infrastructure.monitoring.metrics import (track_business_metrics,
                                                   track_request_metrics)
from src.infrastructure.repositories.checkpoint_repository_impl import \
    CheckpointRepositoryImpl
from src.infrastructure.repositories.unit_repository_impl import \
    UnitRepositoryImpl
from src.infrastructure.security.auth import (init_auth, log_request,
                                              rate_limit, require_api_key,
                                              validate_content_type)
from src.infrastructure.security.middleware import SecurityMiddleware
from src.presentation.controllers.checkpoint_controller import \
    CheckpointController


def configure_logging():
    """Configura el sistema de logging"""
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def create_app():
    """Factory function para crear la aplicación Flask"""

    # Configurar logging
    configure_logging()
    logger = structlog.get_logger(__name__)

    app = Flask(__name__)

    # Configurar CORS
    CORS(app, origins=["*"])

    # Configurar seguridad
    init_auth(app)
    SecurityMiddleware(app)

    # Configurar base de datos
    db = init_database(app)

    # Configurar Celery
    celery.conf.update(
        broker_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        result_backend=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    )

    # Inicializar repositorios
    unit_repository = UnitRepositoryImpl()
    checkpoint_repository = CheckpointRepositoryImpl()

    # Inicializar servicios de dominio
    unit_service = UnitServiceImpl(unit_repository)

    # Inicializar casos de uso
    register_checkpoint_use_case = RegisterCheckpointUseCase(
        unit_repository=unit_repository,
        checkpoint_repository=checkpoint_repository,
        unit_service=unit_service,
    )

    get_tracking_history_use_case = GetTrackingHistoryUseCase(
        unit_repository=unit_repository, checkpoint_repository=checkpoint_repository
    )

    list_units_by_status_use_case = ListUnitsByStatusUseCase(
        unit_repository=unit_repository
    )

    # Inicializar controlador
    checkpoint_controller = CheckpointController(
        register_checkpoint_use_case=register_checkpoint_use_case,
        get_tracking_history_use_case=get_tracking_history_use_case,
        list_units_by_status_use_case=list_units_by_status_use_case,
    )

    # Registrar rutas con seguridad y métricas
    @app.route("/api/v1/checkpoints", methods=["POST"])
    @require_api_key
    @rate_limit(max_requests=1000, window=3600)  # 1000 requests por hora
    @validate_content_type()
    @track_request_metrics
    @track_business_metrics("checkpoint_registration")
    def register_checkpoint():
        return checkpoint_controller.register_checkpoint()

    @app.route("/api/v1/tracking/<tracking_id>", methods=["GET"])
    @require_api_key
    @rate_limit(max_requests=2000, window=3600)  # 2000 requests por hora
    @track_request_metrics
    @track_business_metrics("tracking_history")
    def get_tracking_history(tracking_id):
        return checkpoint_controller.get_tracking_history(tracking_id)

    @app.route("/api/v1/shipments", methods=["GET"])
    @require_api_key
    @rate_limit(max_requests=1000, window=3600)  # 1000 requests por hora
    @track_request_metrics
    @track_business_metrics("list_units")
    def list_units_by_status():
        return checkpoint_controller.list_units_by_status()

    # Health check endpoints
    create_health_endpoints(app)

    # Endpoint para monitorear tareas de Celery
    @app.route("/api/v1/celery/status", methods=["GET"])
    @require_api_key
    def celery_status():
        try:
            from src.infrastructure.external.celery_config import celery

            # Obtener estadísticas del worker
            inspect = celery.control.inspect()
            stats = inspect.stats()
            active_tasks = inspect.active()
            scheduled_tasks = inspect.scheduled()

            return (
                jsonify(
                    {
                        "celery_status": "running",
                        "workers": list(stats.keys()) if stats else [],
                        "active_tasks": active_tasks or {},
                        "scheduled_tasks": scheduled_tasks or {},
                        "broker_url": celery.conf.broker_url,
                        "result_backend": celery.conf.result_backend,
                    }
                ),
                200,
            )
        except Exception as e:
            logger.error("Error obteniendo estado de Celery", error=str(e))
            return jsonify({"celery_status": "error", "error": str(e)}), 500

    # Endpoint de prueba temporal
    @app.route("/test/units", methods=["GET"])
    def test_units():
        try:
            units = unit_repository.find_by_status(UnitStatus.CREATED)
            return (
                jsonify(
                    {
                        "count": len(units),
                        "units": [
                            {"id": u.id, "tracking_id": str(u.tracking_id)}
                            for u in units
                        ],
                    }
                ),
                200,
            )
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # Manejador de errores global
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "not_found", "message": "Endpoint no encontrado"}), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return (
            jsonify({"error": "method_not_allowed", "message": "Método no permitido"}),
            405,
        )

    @app.errorhandler(500)
    def internal_error(error):
        logger.error("Error interno del servidor", error=str(error))
        return (
            jsonify(
                {"error": "internal_error", "message": "Error interno del servidor"}
            ),
            500,
        )

    # Crear tablas de base de datos
    with app.app_context():
        try:
            db.create_all()
            logger.info("Base de datos inicializada correctamente")
        except Exception as e:
            logger.error("Error inicializando base de datos", error=str(e))

    logger.info("Aplicación Flask creada exitosamente")
    return app


# Crear instancia de la aplicación
app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
