import time
from functools import wraps

import structlog
from flask import g, request

logger = structlog.get_logger(__name__)


class SimpleMetrics:
    """Métricas simples sin dependencias externas"""

    def __init__(self):
        self.counters = {}
        self.timers = {}

    def increment_counter(self, name: str, value: int = 1, tags: dict = None):
        """Incrementa un contador"""
        key = self._build_key(name, tags)
        self.counters[key] = self.counters.get(key, 0) + value

        logger.info(
            "metric_counter",
            name=name,
            value=value,
            total=self.counters[key],
            tags=tags or {},
        )

    def record_timing(self, name: str, duration_ms: float, tags: dict = None):
        """Registra un tiempo de ejecución"""
        key = self._build_key(name, tags)
        if key not in self.timers:
            self.timers[key] = []

        self.timers[key].append(duration_ms)

        # Mantener solo los últimos 100 valores
        if len(self.timers[key]) > 100:
            self.timers[key] = self.timers[key][-100:]

        logger.info(
            "metric_timing",
            name=name,
            duration_ms=round(duration_ms, 2),
            tags=tags or {},
        )

    def _build_key(self, name: str, tags: dict = None) -> str:
        """Construye una clave única para la métrica"""
        if not tags:
            return name

        tag_str = "_".join([f"{k}:{v}" for k, v in sorted(tags.items())])
        return f"{name}_{tag_str}"

    def get_counter(self, name: str, tags: dict = None) -> int:
        """Obtiene el valor de un contador"""
        key = self._build_key(name, tags)
        return self.counters.get(key, 0)

    def get_avg_timing(self, name: str, tags: dict = None) -> float:
        """Obtiene el tiempo promedio"""
        key = self._build_key(name, tags)
        timings = self.timers.get(key, [])
        return sum(timings) / len(timings) if timings else 0.0


# Instancia global de métricas
metrics = SimpleMetrics()


def track_request_metrics(f):
    """Decorador para trackear métricas de requests"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()

        # Métricas de entrada
        metrics.increment_counter(
            "requests_total",
            tags={
                "method": request.method,
                "endpoint": request.endpoint or request.path,
            },
        )

        try:
            response = f(*args, **kwargs)

            # Métricas de éxito
            status_code = response[1] if isinstance(response, tuple) else 200
            metrics.increment_counter(
                "requests_success",
                tags={
                    "method": request.method,
                    "endpoint": request.endpoint or request.path,
                    "status_code": str(status_code),
                },
            )

            return response

        except Exception as e:
            # Métricas de error
            metrics.increment_counter(
                "requests_error",
                tags={
                    "method": request.method,
                    "endpoint": request.endpoint or request.path,
                    "error_type": type(e).__name__,
                },
            )
            raise

        finally:
            # Métricas de timing
            duration_ms = (time.time() - start_time) * 1000
            metrics.record_timing(
                "request_duration_ms",
                duration_ms,
                tags={
                    "method": request.method,
                    "endpoint": request.endpoint or request.path,
                },
            )

    return decorated_function


def track_business_metrics(metric_name: str, tags: dict = None):
    """Decorador para trackear métricas de negocio"""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()

            try:
                result = f(*args, **kwargs)

                # Métrica de éxito
                metrics.increment_counter(f"{metric_name}_success", tags=tags)

                return result

            except Exception as e:
                # Métrica de error
                metrics.increment_counter(
                    f"{metric_name}_error",
                    tags={**(tags or {}), "error_type": type(e).__name__},
                )
                raise

            finally:
                # Métrica de timing
                duration_ms = (time.time() - start_time) * 1000
                metrics.record_timing(
                    f"{metric_name}_duration_ms", duration_ms, tags=tags
                )

        return decorated_function

    return decorator
