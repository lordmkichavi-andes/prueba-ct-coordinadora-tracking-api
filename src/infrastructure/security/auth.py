from functools import wraps
from flask import request, jsonify, current_app
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token
from datetime import timedelta
import os
import structlog

logger = structlog.get_logger(__name__)


def init_auth(app):
    """Inicializa la autenticación JWT"""
    
    # Configurar JWT
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    app.config['JWT_ALGORITHM'] = 'HS256'
    
    jwt = JWTManager(app)
    
    # Manejadores de errores JWT
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'error': 'token_expired',
            'message': 'Token expirado'
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'error': 'invalid_token',
            'message': 'Token inválido'
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'error': 'authorization_required',
            'message': 'Token de autorización requerido'
        }), 401
    
    return jwt


def require_api_key(f):
    """Decorador para requerir API key"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        expected_api_key = os.getenv('API_KEY', 'default-api-key')
        
        if not api_key or api_key != expected_api_key:
            logger.warning(
                "Intento de acceso con API key inválida",
                ip=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            return jsonify({
                'error': 'invalid_api_key',
                'message': 'API key inválida'
            }), 401
        
        return f(*args, **kwargs)
    
    return decorated_function


def rate_limit(max_requests=100, window=3600):
    """Decorador para limitar la tasa de requests"""
    from collections import defaultdict, deque
    import time
    
    # En producción, esto debería usar Redis
    request_counts = defaultdict(deque)
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = request.remote_addr
            current_time = time.time()
            
            # Limpiar requests antiguos
            while request_counts[client_ip] and request_counts[client_ip][0] <= current_time - window:
                request_counts[client_ip].popleft()
            
            # Verificar límite
            if len(request_counts[client_ip]) >= max_requests:
                logger.warning(
                    "Rate limit excedido",
                    ip=client_ip,
                    requests=len(request_counts[client_ip])
                )
                return jsonify({
                    'error': 'rate_limit_exceeded',
                    'message': f'Máximo {max_requests} requests por hora'
                }), 429
            
            # Agregar request actual
            request_counts[client_ip].append(current_time)
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator


def validate_content_type(expected_type='application/json'):
    """Decorador para validar content type"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.method in ['POST', 'PUT', 'PATCH']:
                content_type = request.headers.get('Content-Type', '')
                if not content_type.startswith(expected_type):
                    return jsonify({
                        'error': 'invalid_content_type',
                        'message': f'Content-Type debe ser {expected_type}'
                    }), 400
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator


def log_request(f):
    """Decorador para loggear requests"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        logger.info(
            "Request recibido",
            method=request.method,
            path=request.path,
            ip=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        response = f(*args, **kwargs)
        
        # Log response status
        if isinstance(response, tuple):
            status_code = response[1]
        else:
            status_code = 200
        
        logger.info(
            "Response enviado",
            method=request.method,
            path=request.path,
            status_code=status_code
        )
        
        return response
    
    return decorated_function

