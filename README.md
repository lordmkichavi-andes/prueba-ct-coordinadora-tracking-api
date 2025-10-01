# Coordinadora Tracking API - Bloque 1

Sistema de tracking de unidades para Coordinadora, implementando Clean Architecture con Python, Flask, Celery y PostgreSQL.

## 🏗️ Arquitectura

El proyecto implementa **Clean Architecture** con las siguientes capas:

- **Domain Layer**: Entidades, Value Objects y reglas de negocio
- **Application Layer**: Casos de uso y servicios de aplicación
- **Infrastructure Layer**: Implementaciones concretas (SQLAlchemy, Redis, Celery)
- **Presentation Layer**: API REST con Flask

## 🚀 Tecnologías

- **Python 3.11**: Lenguaje de programación
- **Flask**: Framework web
- **PostgreSQL**: Base de datos relacional
- **Redis**: Cache y cola de mensajes
- **Celery**: Procesamiento asíncrono
- **SQLAlchemy**: ORM
- **Marshmallow**: Validación y serialización
- **Docker & Docker Compose**: Containerización
- **pytest**: Testing framework

## 📋 Funcionalidades Implementadas

### API Endpoints

- `POST /api/v1/checkpoints` - Registrar checkpoint de unidad
- `GET /api/v1/tracking/:trackingId` - Consultar historial de tracking
- `GET /api/v1/shipments` - Listar unidades por estado

## 🛠️ Configuración

### Prerrequisitos

- Docker y Docker Compose

### Configuración Inicial

1. **Clonar el repositorio:**
```bash
git clone https://github.com/lordmkichavi-andes/prueba-ct-coordinadora-tracking-api.git
cd prueba-ct-coordinadora-tracking-api
```

2. **Configurar variables de entorno:**
```bash
cp env.example .env
```

4. **Construir y ejecutar servicios:**
```bash
docker-compose up --build
```

### Verificar Instalación

```bash
# Verificar salud de la API
curl http://localhost:8000/health

# Verificar estado de Celery
curl -H "X-API-Key: test-api-key" http://localhost:8000/api/v1/celery/status
```

## 🧪 Testing

### Ejecutar Pruebas

```bash
# Ejecutar todas las pruebas
docker-compose exec app python3 -m pytest

# Pruebas con coverage
docker-compose exec app python3 -m pytest --cov=src

# Pruebas unitarias solamente
docker-compose exec app python3 -m pytest tests/unit/

# Pruebas de integración solamente
docker-compose exec app python3 -m pytest tests/integration/
```

### Pruebas de API con cURL

```bash
# Registrar checkpoint
curl -X POST http://localhost:8000/api/v1/checkpoints \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-api-key" \
  -d '{
    "tracking_id": "TEST123456",
    "status": "CREATED",
    "location": "Bogotá, Colombia",
    "description": "Paquete creado",
    "timestamp": "2024-01-15T10:30:00Z"
  }'

# Consultar tracking
curl -H "X-API-Key: test-api-key" \
  http://localhost:8000/api/v1/tracking/TEST123456

# Listar unidades por estado
curl -H "X-API-Key: test-api-key" \
  "http://localhost:8000/api/v1/shipments?status=CREATED"
```

## 📊 Métricas y Monitoreo

- **Health Check**: `GET /health`
- **Métricas de negocio**: `GET /metrics/business`
- **Estado de Celery**: `GET /api/v1/celery/status`

## 📚 Documentación

- [Arquitectura del Sistema](docs/architecture.md)
- [Diagramas C4](docs/c4-diagrams.md)

## 🏛️ Estructura del Proyecto

```
coordinadora/
├── src/
│   ├── domain/              # Capa de Dominio
│   │   ├── entities/        # Entidades de negocio
│   │   ├── value_objects/   # Objetos de valor
│   │   └── repositories/    # Interfaces de repositorios
│   ├── application/         # Capa de Aplicación
│   │   ├── use_cases/       # Casos de uso
│   │   ├── services/        # Servicios de aplicación
│   │   └── interfaces/      # Interfaces de servicios
│   ├── infrastructure/      # Capa de Infraestructura
│   │   ├── database/        # Configuración de BD
│   │   ├── repositories/    # Implementaciones de repositorios
│   │   ├── external/        # Servicios externos (Celery)
│   │   ├── security/        # Seguridad y autenticación
│   │   └── monitoring/      # Métricas y logging
│   └── presentation/        # Capa de Presentación
│       ├── controllers/     # Controladores de API
│       └── schemas/         # Esquemas de validación
├── tests/                   # Pruebas
│   ├── unit/               # Pruebas unitarias
│   └── integration/        # Pruebas de integración
├── docs/                   # Documentación
├── docker-compose.yml      # Orquestación de servicios
├── Dockerfile             # Imagen de la aplicación
├── requirements.txt       # Dependencias Python
└── README.md             # Este archivo
```

## 🚀 Despliegue

### Variables de Entorno Requeridas

```bash
API_KEY=your-api-key-here
DATABASE_URL=postgresql://user:password@db:5432/tracking_db
REDIS_URL=redis://redis:6379/0
```

### Docker Compose Services

- **app**: Aplicación Flask (Puerto 8000)
- **celery**: Worker de Celery
- **db**: PostgreSQL (Puerto 5432)
- **redis**: Redis (Puerto 6379)

## 📄 Licencia

Este proyecto es parte del reto técnico de Coordinadora.

---

**Desarrollado por**: Javier D. Fajardo R.
**Fecha**: 27 de Septiembre de 2025
**Versión**: 1.0.0
