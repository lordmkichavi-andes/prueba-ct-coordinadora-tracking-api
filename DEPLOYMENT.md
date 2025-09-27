# 🚀 Guía de Despliegue - API de Tracking

Esta guía explica cómo desplegar la API de Tracking usando Docker y GitHub Actions.

## 🚀 Inicio Rápido

¿Quieres probar la API de Tracking rápidamente? Sigue estos pasos:

```bash
# 1. Clonar y configurar
git clone <tu-repositorio>
cd coordinadora
cp env.example .env

# 2. Levantar servicios
docker-compose up -d

# 3. Verificar que funciona
curl http://localhost:8000/health

# 4. Probar la API
curl -H "X-API-Key: test-api-key" "http://localhost:8000/api/v1/shipments?status=CREATED"
```

¡Listo! En menos de 2 minutos tienes la API funcionando. 🎉

## 📚 Estructura del Proyecto

```
coordinadora/
├── 🐳 Contenedores
│   ├── Dockerfile              # Imagen de la aplicación
│   ├── Dockerfile.prod         # Imagen optimizada para producción
│   ├── docker-compose.yml      # Servicios de desarrollo
│   └── docker-compose.prod.yml # Servicios de producción
├── 🔄 CI/CD
│   └── .github/workflows/      # GitHub Actions
│       ├── ci-cd.yml          # Pipeline principal
│       ├── pr-checks.yml      # Validación de PRs
│       └── release.yml        # Releases automáticos
├── 🌐 Proxy
│   ├── nginx.conf             # Configuración de desarrollo
│   └── nginx.prod.conf        # Configuración de producción
├── ⚙️ Configuración
│   ├── .env.example           # Variables de entorno de ejemplo
│   ├── requirements.txt       # Dependencias de Python
│   └── .dockerignore          # Archivos ignorados en Docker
└── 📖 Documentación
    ├── DEPLOYMENT.md          # Esta guía
    ├── docs/api-documentation.md
    └── docs/testing.md
```

## 📋 Requisitos Previos

- Docker y Docker Compose instalados
- Git configurado
- Cuenta de GitHub con permisos para crear repositorios

## 🐳 Despliegue Local con Docker

### 1. Desarrollo
```bash
# Clonar el repositorio
git clone <tu-repositorio>
cd coordinadora

# Copiar archivo de variables de entorno
cp env.example .env

# Editar variables de entorno según sea necesario
nano .env

# Levantar servicios
docker-compose up -d

# Verificar que todo esté funcionando
curl http://localhost:8000/health
```

### 2. Producción
```bash
# Usar docker-compose de producción
docker-compose -f docker-compose.prod.yml up -d

# Verificar despliegue
curl http://localhost/health
```

## 🔄 CI/CD con GitHub Actions

### Workflows Incluidos

1. **CI/CD Principal** (`.github/workflows/ci-cd.yml`)
   - Ejecuta tests y análisis de código
   - Construye y publica imagen Docker
   - Despliega automáticamente en staging y producción

2. **Validación de PR** (`.github/workflows/pr-checks.yml`)
   - Valida código en Pull Requests
   - Ejecuta preview de la aplicación
   - Comenta resultados en el PR

3. **Releases** (`.github/workflows/release.yml`)
   - Crea releases automáticos con tags
   - Genera changelog automáticamente
   - Publica imágenes Docker etiquetadas

### Configuración de Secrets

En tu repositorio de GitHub, ve a Settings > Secrets y agrega:

```
STAGING_URL=https://tu-app-staging.com
PRODUCTION_URL=https://tu-app-produccion.com
```

### Crear un Release

```bash
# Crear tag y push
git tag v1.0.0
git push origin v1.0.0

# GitHub Actions creará automáticamente el release
```

## 📊 Monitoreo Básico

### Health Checks
- **Aplicación**: `GET /health`
- **Base de datos**: Verificación automática en Docker
- **Redis**: Verificación automática en Docker

### Logs
```bash
# Ver logs de la aplicación
docker-compose logs -f app

# Ver logs de todos los servicios
docker-compose logs -f

# Ver logs de producción
docker-compose -f docker-compose.prod.yml logs -f
```

## 🔧 Comandos Útiles

```bash
# Reconstruir imagen
docker-compose build --no-cache

# Reiniciar servicios
docker-compose restart

# Ejecutar tests
docker-compose exec app pytest

# Acceder a la base de datos
docker-compose exec db psql -U tracking_user -d tracking_db

# Ver estado de contenedores
docker-compose ps

# Limpiar contenedores parados
docker-compose down
docker system prune -f
```

## 🚨 Solución de Problemas

### La aplicación no inicia
```bash
# Verificar logs
docker-compose logs app

# Verificar conectividad de base de datos
docker-compose exec app python -c "import psycopg2; print('DB OK')"
```

### Problemas de memoria
```bash
# Verificar uso de memoria
docker stats

# Ajustar límites en docker-compose.prod.yml
```

### Tests fallando en CI/CD
- Verificar que todas las dependencias estén en `requirements.txt`
- Revisar variables de entorno en los workflows
- Verificar que los servicios de test estén funcionando

## 📈 Escalabilidad

Para manejar más carga:

1. **Aumentar workers de Gunicorn**:
   ```yaml
   # En docker-compose.prod.yml
   command: ["gunicorn", "--workers", "8", ...]
   ```

2. **Escalar horizontalmente**:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d --scale app=3
   ```

3. **Optimizar base de datos**:
   - Configurar connection pooling
   - Añadir índices apropiados
   - Considerar read replicas

## 🔒 Seguridad

- ✅ Usuario no-root en contenedores
- ✅ Rate limiting en Nginx
- ✅ Headers de seguridad
- ✅ Variables de entorno para secrets
- ✅ Health checks configurados
- ✅ Límites de recursos en contenedores

## 🧪 Pruebas del Sistema

### Verificar que Todo Funciona

Después de desplegar, puedes verificar que el sistema funciona correctamente ejecutando estas pruebas:

#### 1. Prueba de Construcción de Imagen Docker
```bash
# Construir imagen de prueba
docker build -t tracking-api-test .

# Verificar que la imagen se creó
docker images | grep tracking-api-test
```

#### 2. Prueba de Docker Compose Local
```bash
# Levantar servicios de desarrollo
docker-compose up -d

# Verificar estado de contenedores
docker-compose ps

# Todos los servicios deberían estar "healthy" o "Up"
```

#### 3. Prueba de Health Checks
```bash
# Health check de la aplicación
curl -f http://localhost:8000/health

# Respuesta esperada:
# {"service":"tracking-api","status":"healthy","timestamp":"...","version":"1.0.0"}
```

#### 4. Prueba de Endpoints de la API
```bash
# Listar unidades por estado
curl -H "X-API-Key: test-api-key" "http://localhost:8000/api/v1/shipments?status=CREATED"

# Obtener historial de tracking
curl -H "X-API-Key: test-api-key" "http://localhost:8000/api/v1/tracking/API123456"

# Registrar checkpoint
curl -X POST -H "X-API-Key: test-api-key" -H "Content-Type: application/json" \
  -d '{"tracking_id": "API123456", "checkpoint_data": {"status": "PICKED_UP", "location": "Centro de distribución"}}' \
  http://localhost:8000/api/v1/checkpoints

# Estado de Celery
curl -H "X-API-Key: test-api-key" "http://localhost:8000/api/v1/celery/status"
```

#### 5. Prueba de Configuración de Producción
```bash
# Detener servicios de desarrollo
docker-compose down

# Levantar servicios de producción
docker-compose -f docker-compose.prod.yml up -d

# Verificar escalabilidad (debería haber 2 instancias de app y celery)
docker-compose -f docker-compose.prod.yml ps

# Probar a través de Nginx
curl -f http://localhost/health
```

### Resultados Esperados

✅ **Construcción de imagen**: Imagen de ~327MB creada exitosamente  
✅ **Docker Compose**: Todos los servicios en estado "healthy"  
✅ **Health checks**: Respuesta JSON con status "healthy"  
✅ **API endpoints**: Respuestas JSON válidas para todos los endpoints  
✅ **Producción**: 2 instancias de app + 2 de Celery + Nginx funcionando  
✅ **Escalabilidad**: Load balancing entre múltiples instancias  

### Solución de Problemas en las Pruebas

#### Error de conexión a base de datos
```bash
# Verificar variables de entorno
cat .env

# Asegurarse de que estén configuradas:
# POSTGRES_DB=tracking_db
# POSTGRES_USER=tracking_user  
# POSTGRES_PASSWORD=tracking_password
```

#### Error 401 (Unauthorized)
```bash
# Verificar que API_KEY esté configurada
echo "API_KEY=test-api-key" >> .env

# Reiniciar servicios
docker-compose restart app
```

#### Health checks fallando
```bash
# Verificar logs de la aplicación
docker-compose logs app

# Esperar más tiempo para que los servicios se estabilicen
sleep 30
```

### Métricas de Rendimiento

- **Tiempo de construcción**: ~65 segundos
- **Tamaño de imagen**: ~327MB
- **Tiempo de inicio**: ~30 segundos
- **Servicios en producción**: 7 contenedores
- **Escalabilidad**: 2 instancias de app + 2 de Celery

## 🎯 Casos de Uso Comunes

### Desarrollo Local
```bash
# Levantar solo la base de datos para desarrollo
docker-compose up -d db redis

# Ejecutar la aplicación localmente (sin Docker)
python app.py
```

### Testing
```bash
# Ejecutar tests unitarios
docker-compose exec app pytest tests/unit/

# Ejecutar tests de integración
docker-compose exec app pytest tests/integration/

# Ejecutar todos los tests con cobertura
docker-compose exec app pytest --cov=src
```

### Debugging
```bash
# Ver logs en tiempo real
docker-compose logs -f app

# Acceder al contenedor para debugging
docker-compose exec app bash

# Verificar conectividad de servicios
docker-compose exec app python -c "import psycopg2; print('DB OK')"
```

### Producción
```bash
# Despliegue con escalado
docker-compose -f docker-compose.prod.yml up -d --scale app=3

# Ver métricas de recursos
docker stats

# Backup de base de datos
docker-compose exec db pg_dump -U tracking_user tracking_db > backup.sql
```

## 📝 Notas Importantes

- La imagen Docker se publica automáticamente en GitHub Container Registry
- Los releases se crean automáticamente con tags
- El despliegue en producción requiere aprobación manual
- Todos los contenedores tienen health checks configurados
- Las pruebas deben ejecutarse después de cada despliegue para verificar funcionalidad
- El sistema está optimizado para manejar 300,000+ guías/día según los requisitos
