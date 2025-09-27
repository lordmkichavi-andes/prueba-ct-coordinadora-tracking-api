# Arquitectura del Sistema de Tracking

## Diagrama C4 - Nivel 1: Contexto del Sistema

```mermaid
graph TB
    subgraph "Sistema de Tracking de Paquetes"
        TS[Tracking System API]
    end
    
    subgraph "Usuarios Externos"
        OP[Operadores Logísticos]
        CS[Clientes]
        ADM[Administradores]
    end
    
    subgraph "Sistemas Externos"
        WMS[Warehouse Management]
        TMS[Transport Management]
        NOT[Notification Service]
    end
    
    OP -->|Registra checkpoints| TS
    CS -->|Consulta tracking| TS
    ADM -->|Administra sistema| TS
    
    TS -->|Integra con| WMS
    TS -->|Integra con| TMS
    TS -->|Envía notificaciones| NOT
```

## Diagrama C4 - Nivel 2: Contenedores

```mermaid
graph TB
    subgraph "Sistema de Tracking"
        WEB[Web Application<br/>Flask + Python]
        API[REST API<br/>Flask]
        WORKER[Celery Workers<br/>Python]
        DB[(PostgreSQL<br/>Database)]
        CACHE[(Redis<br/>Cache & Queue)]
    end
    
    subgraph "Usuarios"
        USER[Usuarios]
    end
    
    subgraph "Sistemas Externos"
        EXT[External Systems]
    end
    
    USER -->|HTTPS| WEB
    USER -->|HTTPS| API
    EXT -->|HTTPS| API
    
    API -->|SQL| DB
    API -->|Redis Protocol| CACHE
    WORKER -->|SQL| DB
    WORKER -->|Redis Protocol| CACHE
    API -->|Queue Tasks| WORKER
```

## Diagrama C4 - Nivel 3: Componentes

```mermaid
graph TB
    subgraph "API Container"
        CTRL[Controllers<br/>Flask Routes]
        UC[Use Cases<br/>Business Logic]
        SVC[Domain Services]
        REPO[Repositories]
        AUTH[Security<br/>Auth & Rate Limiting]
        METRICS[Metrics<br/>& Logging]
    end
    
    subgraph "Database"
        UNITS[Units Table]
        CHECKPOINTS[Checkpoints Table]
        SHIPMENTS[Shipments Table]
    end
    
    subgraph "Cache & Queue"
        QUEUE[Celery Queue]
        CACHE_DATA[Cache Data]
    end
    
    CTRL --> UC
    UC --> SVC
    UC --> REPO
    CTRL --> AUTH
    CTRL --> METRICS
    
    REPO --> UNITS
    REPO --> CHECKPOINTS
    REPO --> SHIPMENTS
    
    UC --> QUEUE
    METRICS --> CACHE_DATA
```

## Diagrama C4 - Nivel 4: Código (Clean Architecture)

```mermaid
graph TB
    subgraph "Presentation Layer"
        CTRL[Controllers]
        SCHEMA[Schemas]
        MIDDLEWARE[Middleware]
    end
    
    subgraph "Application Layer"
        UC[Use Cases]
        INTERFACES[Interfaces]
        SERVICES[Services]
    end
    
    subgraph "Domain Layer"
        ENTITIES[Entities]
        VO[Value Objects]
        REPO_INT[Repository Interfaces]
    end
    
    subgraph "Infrastructure Layer"
        REPO_IMPL[Repository Implementations]
        DB[Database]
        EXTERNAL[External Services]
    end
    
    CTRL --> UC
    UC --> INTERFACES
    UC --> SERVICES
    INTERFACES --> REPO_INT
    SERVICES --> ENTITIES
    ENTITIES --> VO
    REPO_INT --> REPO_IMPL
    REPO_IMPL --> DB
    EXTERNAL --> DB
```

## Decisiones Arquitectónicas

### 1. Clean Architecture
**Decisión**: Implementar Clean Architecture con separación clara de capas.

**Justificación**:
- Mantenibilidad y testabilidad
- Independencia de frameworks
- Facilita cambios en infraestructura
- Cumple con principios SOLID

### 2. PostgreSQL como Base de Datos Principal
**Decisión**: Usar PostgreSQL para persistencia de datos.

**Justificación**:
- ACID compliance para transacciones críticas
- Escalabilidad horizontal y vertical
- Soporte robusto para consultas complejas
- Compatibilidad con SQLAlchemy

### 3. Redis para Cache y Cola de Tareas
**Decisión**: Usar Redis para cache y cola de mensajes de Celery.

**Justificación**:
- Alto rendimiento para operaciones de cache
- Cola de tareas asíncronas confiable
- Persistencia opcional
- Escalabilidad horizontal

### 4. Celery para Tareas Asíncronas
**Decisión**: Implementar Celery para procesamiento asíncrono.

**Justificación**:
- Procesamiento de checkpoints en background
- Escalabilidad de workers
- Retry automático de tareas fallidas
- Monitoreo de tareas

### 5. API REST con Autenticación por API Key
**Decisión**: Implementar API REST con autenticación por API Key.

**Justificación**:
- Simplicidad de implementación
- Rate limiting por API key
- Seguridad adecuada para el contexto
- Fácil integración con sistemas externos

### 6. Logging Estructurado con structlog
**Decisión**: Usar structlog para logging estructurado.

**Justificación**:
- Facilita análisis de logs
- Integración con sistemas de monitoreo
- Performance optimizado
- Formato JSON para parsing

### 7. Métricas Simples sin Prometheus
**Decisión**: Implementar métricas básicas sin dependencias externas.

**Justificación**:
- Simplicidad para el MVP
- Menos complejidad operacional
- Logging estructurado suficiente
- Fácil de mantener

## Flujo de Datos Principal

### Registro de Checkpoint
1. Cliente envía POST /api/v1/checkpoints
2. Middleware valida API key y rate limiting
3. Controller valida datos de entrada
4. Use Case ejecuta lógica de negocio
5. Repository persiste en base de datos
6. Tarea asíncrona se encola en Celery
7. Response se envía al cliente

### Consulta de Tracking
1. Cliente envía GET /api/v1/tracking/{id}
2. Middleware valida API key
3. Controller extrae tracking ID
4. Use Case busca datos en repositorio
5. Repository consulta base de datos
6. Response con historial se envía al cliente

## Consideraciones de Escalabilidad

### Horizontal
- Múltiples instancias de API con load balancer
- Workers de Celery distribuidos
- Redis Cluster para alta disponibilidad
- PostgreSQL con read replicas

### Vertical
- Optimización de queries con índices
- Cache de consultas frecuentes
- Connection pooling
- Compresión de respuestas

## Monitoreo y Observabilidad

### Logs
- Logging estructurado en JSON
- Niveles de log apropiados
- Correlación de requests con trace IDs

### Métricas
- Contadores de requests por endpoint
- Tiempos de respuesta
- Errores por tipo
- Métricas de negocio (checkpoints por estado)

### Health Checks
- /health - Estado básico
- /health/detailed - Estado detallado de componentes
- /health/ready - Readiness para Kubernetes
- /health/live - Liveness para Kubernetes

