# Diagramas C4 - Sistema de Tracking de Paquetes

## Nivel 1: Contexto del Sistema

```mermaid
graph TB
    subgraph "Sistema de Tracking de Paquetes"
        TS["`**Tracking System**<br/>System<br/>Sistema de tracking de paquetes<br/>con checkpoints`"]
    end
    
    subgraph "Usuarios Externos"
        OP["`**Operadores Logísticos**<br/>Person<br/>Personas que registran<br/>checkpoints`"]
        CS["`**Clientes**<br/>Person<br/>Personas que consultan<br/>el estado de sus paquetes`"]
        ADM["`**Administradores**<br/>Person<br/>Personas que administran<br/>el sistema`"]
    end
    
    subgraph "Sistemas Externos"
        WMS["`**Warehouse Management**<br/>System<br/>Sistema de gestión<br/>de almacenes`"]
        TMS["`**Transport Management**<br/>System<br/>Sistema de gestión<br/>de transporte`"]
        NOT["`**Notification Service**<br/>System<br/>Servicio de notificaciones<br/>para clientes`"]
    end
    
    OP -.->|"`Registra checkpoints`"| TS
    CS -.->|"`Consulta tracking`"| TS
    ADM -.->|"`Administra sistema`"| TS
    
    TS -.->|"`Integra con`"| WMS
    TS -.->|"`Integra con`"| TMS
    TS -.->|"`Envía notificaciones`"| NOT
    
    classDef person fill:#1168bd,stroke:#0b4884,stroke-width:2px,color:#fff
    classDef system fill:#1168bd,stroke:#0b4884,stroke-width:2px,color:#fff
    classDef external fill:#999999,stroke:#595959,stroke-width:2px,color:#fff
    
    class OP,CS,ADM person
    class TS system
    class WMS,TMS,NOT external
```

### Descripción del Contexto

**Sistema Central:**
- **Tracking System API**: El sistema principal que gestiona el tracking de paquetes

**Usuarios Externos:**
- **Operadores Logísticos**: Registran checkpoints durante el proceso logístico
- **Clientes**: Consultan el estado de sus paquetes
- **Administradores**: Gestionan y administran el sistema

**Sistemas Externos:**
- **Warehouse Management (WMS)**: Sistema de gestión de almacenes
- **Transport Management (TMS)**: Sistema de gestión de transporte
- **Notification Service**: Servicio de notificaciones para clientes

---

## Nivel 2: Contenedores

```mermaid
graph TB
    subgraph "Tracking System"
        WEB["`**Web Application**<br/>Container (Flask)<br/>Interfaz web para administradores`"]
        API["`**REST API**<br/>Container (Flask)<br/>API principal para operadores`"]
        WORKER["`**Celery Workers**<br/>Container (Python)<br/>Procesamiento asíncrono`"]
        DB[("`**PostgreSQL**<br/>Container (PostgreSQL)<br/>Base de datos principal`")]
        CACHE[("`**Redis**<br/>Container (Redis)<br/>Cache y cola de mensajes`")]
    end
    
    subgraph "Usuarios"
        USER["`**Usuarios**<br/>Person<br/>Operadores, Clientes<br/>y Administradores`"]
    end
    
    subgraph "Sistemas Externos"
        EXT["`**External Systems**<br/>System<br/>WMS, TMS, Notification<br/>Sistemas externos`"]
    end
    
    USER -.->|"`HTTPS`"| WEB
    USER -.->|"`HTTPS`"| API
    EXT -.->|"`HTTPS`"| API
    
    API -.->|"`SQL`"| DB
    API -.->|"`Redis Protocol`"| CACHE
    WORKER -.->|"`SQL`"| DB
    WORKER -.->|"`Redis Protocol`"| CACHE
    API -.->|"`Queue Tasks`"| WORKER
    
    classDef container fill:#85bbf0,stroke:#0b4884,stroke-width:2px,color:#000
    classDef database fill:#85bbf0,stroke:#0b4884,stroke-width:2px,color:#000
    classDef messagebus fill:#85bbf0,stroke:#0b4884,stroke-width:2px,color:#000
    classDef person fill:#1168bd,stroke:#0b4884,stroke-width:2px,color:#fff
    classDef external fill:#999999,stroke:#595959,stroke-width:2px,color:#fff
    
    class WEB,API,WORKER container
    class DB database
    class CACHE messagebus
    class USER person
    class EXT external
```

### Descripción de Contenedores

**Aplicación Web:**
- **Web Application**: Interfaz web para administradores
- **REST API**: API principal para operadores y sistemas externos
- **Celery Workers**: Procesamiento asíncrono de tareas

**Almacenamiento:**
- **PostgreSQL**: Base de datos principal para persistencia
- **Redis**: Cache y cola de mensajes para Celery

**Comunicación:**
- **HTTPS**: Comunicación segura con usuarios y sistemas externos
- **SQL**: Consultas a la base de datos
- **Redis Protocol**: Comunicación con cache y colas

---

## Nivel 3: Componentes

```mermaid
graph TB
    subgraph "REST API Container"
        CTRL["`**Controllers**<br/>Component (Flask Routes)<br/>Manejo de requests HTTP`"]
        UC["`**Use Cases**<br/>Component (Python Classes)<br/>Lógica de negocio`"]
        SVC["`**Domain Services**<br/>Component (Python Classes)<br/>Servicios de dominio`"]
        REPO["`**Repositories**<br/>Component (SQLAlchemy)<br/>Abstracción de persistencia`"]
        AUTH["`**Security**<br/>Component (Flask Middleware)<br/>Autenticación y autorización`"]
        METRICS["`**Metrics**<br/>Component (Structlog)<br/>Métricas y logging`"]
    end
    
    subgraph "PostgreSQL Database"
        UNITS["`**Units Table**<br/>Component (SQLAlchemy Model)<br/>Información de tracking`"]
        CHECKPOINTS["`**Checkpoints Table**<br/>Component (SQLAlchemy Model)<br/>Historial de estados`"]
        SHIPMENTS["`**Shipments Table**<br/>Component (SQLAlchemy Model)<br/>Agrupaciones de unidades`"]
    end
    
    subgraph "Redis Cache & Queue"
        QUEUE["`**Celery Queue**<br/>Component (Celery Tasks)<br/>Procesamiento asíncrono`"]
        CACHE_DATA["`**Cache Data**<br/>Component (Redis Cache)<br/>Consultas frecuentes`"]
    end
    
    CTRL -.->|"`HTTP`"| UC
    UC -.->|"`Business Logic`"| SVC
    UC -.->|"`Data Access`"| REPO
    CTRL -.->|"`Security`"| AUTH
    CTRL -.->|"`Monitoring`"| METRICS
    
    REPO -.->|"`SQL`"| UNITS
    REPO -.->|"`SQL`"| CHECKPOINTS
    REPO -.->|"`SQL`"| SHIPMENTS
    
    UC -.->|"`Queue Tasks`"| QUEUE
    METRICS -.->|"`Cache`"| CACHE_DATA
    
    classDef component fill:#85bbf0,stroke:#0b4884,stroke-width:2px,color:#000
    classDef database fill:#85bbf0,stroke:#0b4884,stroke-width:2px,color:#000
    classDef queue fill:#85bbf0,stroke:#0b4884,stroke-width:2px,color:#000
    
    class CTRL,UC,SVC,REPO,AUTH,METRICS component
    class UNITS,CHECKPOINTS,SHIPMENTS database
    class QUEUE,CACHE_DATA queue
```

### Descripción de Componentes

**API Container:**
- **Controllers**: Manejan las rutas HTTP y validación de entrada
- **Use Cases**: Contienen la lógica de negocio principal
- **Domain Services**: Servicios específicos del dominio
- **Repositories**: Abstracción del acceso a datos
- **Security**: Autenticación, autorización y rate limiting
- **Metrics**: Logging estructurado y métricas

**Database:**
- **Units Table**: Almacena información de las unidades de tracking
- **Checkpoints Table**: Historial de checkpoints por unidad
- **Shipments Table**: Información de envíos y agrupaciones

**Cache & Queue:**
- **Celery Queue**: Cola de tareas asíncronas
- **Cache Data**: Cache para consultas frecuentes

---

## Nivel 4: Código (Clean Architecture)

```mermaid
graph TB
    subgraph "Presentation Layer"
        CTRL["`**Controllers**<br/>Component (Flask Routes)<br/>Manejo de requests HTTP`"]
        SCHEMA["`**Schemas**<br/>Component (Marshmallow)<br/>Validación y serialización`"]
        MIDDLEWARE["`**Middleware**<br/>Component (Flask Middleware)<br/>Seguridad y logging`"]
    end
    
    subgraph "Application Layer"
        UC["`**Use Cases**<br/>Component (Python Classes)<br/>Casos de uso específicos`"]
        INTERFACES["`**Interfaces**<br/>Component (Python ABC)<br/>Contratos para servicios`"]
        SERVICES["`**Services**<br/>Component (Python Classes)<br/>Servicios de aplicación`"]
    end
    
    subgraph "Domain Layer"
        ENTITIES["`**Entities**<br/>Component (Python Classes)<br/>Unit, Checkpoint, Shipment`"]
        VO["`**Value Objects**<br/>Component (Python Classes)<br/>TrackingId, UnitStatus`"]
        REPO_INT["`**Repository Interfaces**<br/>Component (Python ABC)<br/>Contratos para acceso a datos`"]
    end
    
    subgraph "Infrastructure Layer"
        REPO_IMPL["`**Repository Implementations**<br/>Component (SQLAlchemy)<br/>Implementaciones concretas`"]
        DB["`**Database**<br/>Component (Flask-SQLAlchemy)<br/>Configuración y modelos`"]
        EXTERNAL["`**External Services**<br/>Component (Celery)<br/>Integraciones externas`"]
    end
    
    CTRL -.->|"`HTTP`"| UC
    UC -.->|"`Business Logic`"| INTERFACES
    UC -.->|"`Business Logic`"| SERVICES
    INTERFACES -.->|"`Data Access`"| REPO_INT
    SERVICES -.->|"`Domain Logic`"| ENTITIES
    ENTITIES -.->|"`Composition`"| VO
    REPO_INT -.->|"`Implementation`"| REPO_IMPL
    REPO_IMPL -.->|"`SQL`"| DB
    EXTERNAL -.->|"`Integration`"| DB
    
    classDef presentation fill:#85bbf0,stroke:#0b4884,stroke-width:2px,color:#000
    classDef application fill:#85bbf0,stroke:#0b4884,stroke-width:2px,color:#000
    classDef domain fill:#85bbf0,stroke:#0b4884,stroke-width:2px,color:#000
    classDef infrastructure fill:#85bbf0,stroke:#0b4884,stroke-width:2px,color:#000
    
    class CTRL,SCHEMA,MIDDLEWARE presentation
    class UC,INTERFACES,SERVICES application
    class ENTITIES,VO,REPO_INT domain
    class REPO_IMPL,DB,EXTERNAL infrastructure
```

### Descripción de Capas

**Presentation Layer:**
- **Controllers**: Manejan requests HTTP y responses
- **Schemas**: Validación y serialización de datos
- **Middleware**: Interceptores para seguridad y logging

**Application Layer:**
- **Use Cases**: Casos de uso específicos del negocio
- **Interfaces**: Contratos para servicios externos
- **Services**: Servicios de aplicación

**Domain Layer:**
- **Entities**: Entidades de negocio (Unit, Checkpoint, Shipment)
- **Value Objects**: Objetos de valor (TrackingId, UnitStatus, CheckpointData)
- **Repository Interfaces**: Contratos para acceso a datos

**Infrastructure Layer:**
- **Repository Implementations**: Implementaciones concretas de repositorios
- **Database**: Configuración y modelos de base de datos
- **External Services**: Integraciones con servicios externos

---

## Flujo de Datos Principal

### Registro de Checkpoint

```mermaid
sequenceDiagram
    participant C as Cliente
    participant M as Middleware
    participant CTRL as Controller
    participant UC as Use Case
    participant REPO as Repository
    participant DB as Database
    participant Q as Celery Queue
    
    C->>M: POST /api/v1/checkpoints
    M->>M: Validar API Key
    M->>M: Rate Limiting
    M->>CTRL: Request validado
    CTRL->>CTRL: Validar datos entrada
    CTRL->>UC: Ejecutar caso de uso
    UC->>REPO: Buscar/crear unidad
    REPO->>DB: Consulta/inserción
    DB-->>REPO: Resultado
    REPO-->>UC: Unidad
    UC->>UC: Agregar checkpoint
    UC->>REPO: Guardar cambios
    REPO->>DB: Actualizar datos
    DB-->>REPO: Confirmación
    REPO-->>UC: Unidad actualizada
    UC->>Q: Encolar tarea asíncrona
    UC-->>CTRL: Resultado
    CTRL-->>M: Response
    M-->>C: 201 Created
```

### Consulta de Tracking

```mermaid
sequenceDiagram
    participant C as Cliente
    participant M as Middleware
    participant CTRL as Controller
    participant UC as Use Case
    participant REPO as Repository
    participant DB as Database
    
    C->>M: GET /api/v1/tracking/{id}
    M->>M: Validar API Key
    M->>CTRL: Request validado
    CTRL->>CTRL: Extraer tracking ID
    CTRL->>UC: Buscar historial
    UC->>REPO: Buscar por tracking ID
    REPO->>DB: Consulta con JOINs
    DB-->>REPO: Datos completos
    REPO-->>UC: Unidad con checkpoints
    UC-->>CTRL: Historial completo
    CTRL-->>M: Response
    M-->>C: 200 OK + JSON
```

---

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

---

## Consideraciones de Escalabilidad

### Escalabilidad Horizontal
- Múltiples instancias de API con load balancer
- Workers de Celery distribuidos
- Redis Cluster para alta disponibilidad
- PostgreSQL con read replicas

### Escalabilidad Vertical
- Optimización de queries con índices
- Cache de consultas frecuentes
- Connection pooling
- Compresión de respuestas

---

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
- `/health` - Estado básico
- `/health/detailed` - Estado detallado de componentes
- `/health/ready` - Readiness para Kubernetes
- `/health/live` - Liveness para Kubernetes
