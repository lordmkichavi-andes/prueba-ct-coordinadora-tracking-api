import time

import structlog
from flask import jsonify, request

logger = structlog.get_logger(__name__)


class SecurityMiddleware:
    """Middleware para seguridad de la API"""

    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Inicializa el middleware con la aplicación Flask"""

        @app.before_request
        def before_request():
            """Ejecuta antes de cada request"""
            # Log del request
            request.start_time = time.time()

            # Validar headers de seguridad
            self._validate_security_headers()

            # Validar tamaño del request
            self._validate_request_size()

        @app.after_request
        def after_request(response):
            """Ejecuta después de cada request"""
            # Agregar headers de seguridad
            self._add_security_headers(response)

            # Log del response
            if hasattr(request, "start_time"):
                duration = time.time() - request.start_time
                logger.info(
                    "Request completado",
                    method=request.method,
                    path=request.path,
                    status_code=response.status_code,
                    duration_ms=round(duration * 1000, 2),
                )

            return response

    def _validate_security_headers(self):
        """Valida headers de seguridad requeridos"""
        # Validar User-Agent
        user_agent = request.headers.get("User-Agent")
        if not user_agent:
            logger.warning("Request sin User-Agent", ip=request.remote_addr)

        # Validar Referer para requests POST/PUT/PATCH
        if request.method in ["POST", "PUT", "PATCH"]:
            referer = request.headers.get("Referer")
            if not referer:
                logger.warning(
                    "Request sin Referer",
                    method=request.method,
                    path=request.path,
                    ip=request.remote_addr,
                )

    def _validate_request_size(self):
        """Valida el tamaño del request"""
        content_length = request.headers.get("Content-Length")
        if content_length:
            size = int(content_length)
            max_size = 10 * 1024 * 1024  # 10MB

            if size > max_size:
                logger.warning(
                    "Request demasiado grande",
                    size=size,
                    max_size=max_size,
                    ip=request.remote_addr,
                )
                return (
                    jsonify(
                        {
                            "error": "request_too_large",
                            "message": "Request demasiado grande",
                        }
                    ),
                    413,
                )

    def _add_security_headers(self, response):
        """Agrega headers de seguridad a la respuesta"""
        # Prevenir clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # Prevenir MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Habilitar XSS protection
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Política de referrer
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Content Security Policy
        response.headers["Content-Security-Policy"] = "default-src 'self'"

        # Remover header de servidor
        response.headers.pop("Server", None)

        return response
