from datetime import datetime, timedelta

import structlog
from flask import jsonify

from ..database.database import db
from ..external.celery_config import celery

logger = structlog.get_logger(__name__)


class HealthChecker:
    """Verificador de salud de la aplicación"""

    def __init__(self):
        self.start_time = datetime.utcnow()

    def check_database(self) -> dict:
        """Verifica la salud de la base de datos"""
        try:
            # Ejecutar query simple
            from sqlalchemy import text

            db.session.execute(text("SELECT 1"))
            return {"status": "healthy", "response_time_ms": 0}  # Simplificado
        except Exception as e:
            logger.error("Database health check failed", error=str(e))
            return {"status": "unhealthy", "error": str(e)}

    def check_redis(self) -> dict:
        """Verifica la salud de Redis"""
        try:
            # Verificar conexión a Celery (que usa Redis)
            celery.control.inspect().stats()
            return {"status": "healthy", "response_time_ms": 0}  # Simplificado
        except Exception as e:
            logger.error("Redis health check failed", error=str(e))
            return {"status": "unhealthy", "error": str(e)}

    def check_celery_workers(self) -> dict:
        """Verifica la salud de los workers de Celery"""
        try:
            stats = celery.control.inspect().stats()
            if stats:
                worker_count = len(stats)
                return {
                    "status": "healthy",
                    "worker_count": worker_count,
                    "workers": list(stats.keys()),
                }
            else:
                return {"status": "unhealthy", "error": "No workers found"}
        except Exception as e:
            logger.error("Celery workers health check failed", error=str(e))
            return {"status": "unhealthy", "error": str(e)}

    def get_application_health(self) -> dict:
        """Obtiene el estado general de salud de la aplicación"""
        uptime = datetime.utcnow() - self.start_time

        # Verificar componentes
        database_health = self.check_database()
        redis_health = self.check_redis()
        celery_health = self.check_celery_workers()

        # Determinar estado general
        all_healthy = all(
            [
                database_health["status"] == "healthy",
                redis_health["status"] == "healthy",
                celery_health["status"] == "healthy",
            ]
        )

        overall_status = "healthy" if all_healthy else "unhealthy"

        return {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": int(uptime.total_seconds()),
            "version": "1.0.0",
            "components": {
                "database": database_health,
                "redis": redis_health,
                "celery": celery_health,
            },
        }


# Instancia global del health checker
health_checker = HealthChecker()


def create_health_endpoints(app):
    """Crea los endpoints de health check"""

    @app.route("/health", methods=["GET"])
    def health_check():
        """Endpoint básico de salud"""
        return (
            jsonify(
                {
                    "status": "healthy",
                    "service": "tracking-api",
                    "version": "1.0.0",
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ),
            200,
        )

    @app.route("/health/detailed", methods=["GET"])
    def detailed_health_check():
        """Endpoint detallado de salud"""
        health_data = health_checker.get_application_health()
        status_code = 200 if health_data["status"] == "healthy" else 503

        return jsonify(health_data), status_code

    @app.route("/health/ready", methods=["GET"])
    def readiness_check():
        """Endpoint de readiness (Kubernetes)"""
        health_data = health_checker.get_application_health()

        if health_data["status"] == "healthy":
            return jsonify({"status": "ready"}), 200
        else:
            return jsonify({"status": "not ready"}), 503

    @app.route("/health/live", methods=["GET"])
    def liveness_check():
        """Endpoint de liveness (Kubernetes)"""
        return jsonify({"status": "alive"}), 200
