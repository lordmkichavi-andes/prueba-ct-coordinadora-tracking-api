# Documentación de Pruebas - Coordinadora Tracking API

## 🧪 Estrategia de Testing

El proyecto implementa una estrategia de testing completa que incluye **pruebas unitarias** y **pruebas de integración** siguiendo las mejores prácticas de Clean Architecture.

### 📊 Cobertura de Pruebas

- **Pruebas Unitarias**: Dominio, casos de uso y servicios
- **Pruebas de Integración**: APIs, base de datos y servicios externos
- **Mocks y Fixtures**: Para aislamiento y reutilización
- **Docker Testing**: Ambiente aislado para pruebas

## 🏗️ Estructura de Pruebas

```
tests/
├── unit/                    # Pruebas Unitarias
│   ├── test_domain_entities.py    # Entidades de dominio
│   └── test_use_cases.py          # Casos de uso
├── integration/             # Pruebas de Integración
│   └── test_api_endpoints.py     # Endpoints de API
└── conftest.py             # Fixtures y configuración
```

## 🔬 Pruebas Unitarias

### Dominio - Entidades de Negocio

**Archivo**: `tests/unit/test_domain_entities.py`

#### Unit Entity Tests

```python
def test_unit_creation():
    """Verifica la creación correcta de una unidad"""
    tracking_id = TrackingId("TEST123456")
    unit = Unit(tracking_id)
    
    assert unit.tracking_id == tracking_id
    assert unit.status == UnitStatus.CREATED
    assert len(unit.checkpoints) == 0

def test_unit_status_transitions():
    """Verifica las transiciones válidas de estado"""
    unit = Unit(TrackingId("TEST123456"))
    
    # Transición válida: CREATED -> PICKED_UP
    unit.update_status(UnitStatus.PICKED_UP)
    assert unit.status == UnitStatus.PICKED_UP
    
    # Transición válida: PICKED_UP -> IN_TRANSIT
    unit.update_status(UnitStatus.IN_TRANSIT)
    assert unit.status == UnitStatus.IN_TRANSIT

def test_unit_invalid_status_transition():
    """Verifica que las transiciones inválidas lancen excepción"""
    unit = Unit(TrackingId("TEST123456"))
    
    with pytest.raises(ValueError, match="No se puede cambiar de CREATED a DELIVERED"):
        unit.update_status(UnitStatus.DELIVERED)

def test_unit_add_checkpoint():
    """Verifica la adición de checkpoints"""
    unit = Unit(TrackingId("TEST123456"))
    checkpoint_data = CheckpointData(
        status=UnitStatus.PICKED_UP,
        location="Bogotá",
        description="Paquete recogido",
        timestamp=datetime.now()
    )
    
    unit.add_checkpoint(checkpoint_data)
    
    assert len(unit.checkpoints) == 1
    assert unit.status == UnitStatus.PICKED_UP
```

#### ✅ Checkpoint Entity Tests

```python
def test_checkpoint_creation():
    """Verifica la creación correcta de un checkpoint"""
    tracking_id = TrackingId("TEST123456")
    checkpoint_data = CheckpointData(
        status=UnitStatus.CREATED,
        location="Bogotá",
        description="Paquete creado",
        timestamp=datetime.now()
    )
    
    checkpoint = Checkpoint(tracking_id, checkpoint_data)
    
    assert checkpoint.tracking_id == tracking_id
    assert checkpoint.status == UnitStatus.CREATED
    assert checkpoint.location == "Bogotá"
```

#### ✅ Value Objects Tests

```python
def test_tracking_id_validation():
    """Verifica la validación del tracking ID"""
    # Tracking ID válido
    valid_id = TrackingId("TEST123456")
    assert str(valid_id) == "TEST123456"
    
    # Tracking ID inválido
    with pytest.raises(ValueError, match="Tracking ID debe tener al menos 6 caracteres"):
        TrackingId("123")

def test_unit_status_enum():
    """Verifica el enum de estados"""
    assert UnitStatus.CREATED.value == "CREATED"
    assert UnitStatus.PICKED_UP.value == "PICKED_UP"
    assert UnitStatus.DELIVERED.value == "DELIVERED"
```

### Casos de Uso - Lógica de Aplicación

**Archivo**: `tests/unit/test_use_cases.py`

#### ✅ RegisterCheckpoint Use Case Tests

```python
def test_register_checkpoint_success():
    """Verifica el registro exitoso de un checkpoint"""
    # Arrange
    tracking_id = TrackingId("TEST123456")
    checkpoint_data = CheckpointData(
        status=UnitStatus.PICKED_UP,
        location="Bogotá",
        description="Paquete recogido",
        timestamp=datetime.now()
    )
    
    # Act
    result = self.register_checkpoint_use_case.execute(tracking_id, checkpoint_data)
    
    # Assert
    assert result["success"] is True
    assert result["unit_id"] is not None
    self.unit_repository.save.assert_called_once()

def test_register_checkpoint_unit_not_found():
    """Verifica la creación automática de unidad cuando no existe"""
    tracking_id = TrackingId("NEW123456")
    checkpoint_data = CheckpointData(
        status=UnitStatus.CREATED,
        location="Bogotá",
        description="Nueva unidad",
        timestamp=datetime.now()
    )
    
    # Mock: Unidad no existe
    self.unit_repository.find_by_tracking_id.return_value = None
    
    # Act
    result = self.register_checkpoint_use_case.execute(tracking_id, checkpoint_data)
    
    # Assert
    assert result["success"] is True
    assert self.unit_repository.save.call_count == 2  # Crear + actualizar
```

#### ✅ GetTrackingHistory Use Case Tests

```python
def test_get_tracking_history_success():
    """Verifica la obtención exitosa del historial"""
    # Arrange
    tracking_id = TrackingId("TEST123456")
    unit = Unit(tracking_id)
    unit.add_checkpoint(CheckpointData(
        status=UnitStatus.CREATED,
        location="Bogotá",
        description="Creado",
        timestamp=datetime.now()
    ))
    
    self.unit_repository.find_by_tracking_id.return_value = unit
    
    # Act
    result = self.get_tracking_use_case.execute(tracking_id)
    
    # Assert
    assert result["success"] is True
    assert len(result["checkpoints"]) == 1
    assert result["current_status"] == UnitStatus.CREATED.value
```

#### ✅ ListUnitsByStatus Use Case Tests

```python
def test_list_units_by_status_success():
    """Verifica el listado de unidades por estado"""
    # Arrange
    units = [
        Unit(TrackingId("TEST001")),
        Unit(TrackingId("TEST002"))
    ]
    self.unit_repository.find_by_status.return_value = units
    
    # Act
    result = self.list_units_use_case.execute(UnitStatus.CREATED)
    
    # Assert
    assert result["success"] is True
    assert len(result["units"]) == 2
```

## 🔗 Pruebas de Integración

### API Endpoints

**Archivo**: `tests/integration/test_api_endpoints.py`

#### ✅ Checkpoint Registration Tests

```python
def test_register_checkpoint_success():
    """Verifica el registro exitoso de checkpoint via API"""
    # Arrange: Crear unidad inicial
    response = self.client.post('/api/v1/checkpoints',
        json={
            "tracking_id": "TEST123456",
            "status": "CREATED",
            "location": "Bogotá, Colombia",
            "description": "Paquete creado",
            "timestamp": "2024-01-15T10:30:00Z"
        },
        headers={"X-API-Key": "test-api-key"}
    )
    assert response.status_code == 201
    
    # Act: Agregar checkpoint
    response = self.client.post('/api/v1/checkpoints',
        json={
            "tracking_id": "TEST123456",
            "status": "PICKED_UP",
            "location": "Medellín, Colombia",
            "description": "Paquete recogido",
            "timestamp": "2024-01-15T11:30:00Z"
        },
        headers={"X-API-Key": "test-api-key"}
    )
    
    # Assert
    assert response.status_code == 201
    data = response.get_json()
    assert data["success"] is True
    assert data["message"] == "Checkpoint registrado exitosamente"

def test_register_checkpoint_invalid_data():
    """Verifica validación de datos inválidos"""
    response = self.client.post('/api/v1/checkpoints',
        json={
            "tracking_id": "123",  # Muy corto
            "status": "INVALID",
            "location": "",
            "description": "Test"
        },
        headers={"X-API-Key": "test-api-key"}
    )
    
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "validation_error"

def test_register_checkpoint_unauthorized():
    """Verifica autenticación con API key"""
    response = self.client.post('/api/v1/checkpoints',
        json={
            "tracking_id": "TEST123456",
            "status": "CREATED",
            "location": "Bogotá",
            "description": "Test"
        }
        # Sin X-API-Key header
    )
    
    assert response.status_code == 401
    data = response.get_json()
    assert data["error"] == "invalid_api_key"
```

#### ✅ Tracking History Tests

```python
def test_get_tracking_history_success():
    """Verifica la consulta exitosa de historial"""
    # Arrange: Crear unidad y checkpoint
    self.client.post('/api/v1/checkpoints',
        json={
            "tracking_id": "TEST123456",
            "status": "CREATED",
            "location": "Bogotá",
            "description": "Creado",
            "timestamp": "2024-01-15T10:30:00Z"
        },
        headers={"X-API-Key": "test-api-key"}
    )
    
    # Act
    response = self.client.get('/api/v1/tracking/TEST123456',
        headers={"X-API-Key": "test-api-key"}
    )
    
    # Assert
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["tracking_id"] == "TEST123456"
    assert len(data["checkpoints"]) == 1
    assert data["current_status"] == "CREATED"

def test_get_tracking_history_not_found():
    """Verifica manejo de tracking ID no encontrado"""
    response = self.client.get('/api/v1/tracking/NONEXISTENT456',
        headers={"X-API-Key": "test-api-key"}
    )
    
    assert response.status_code == 404
    data = response.get_json()
    assert data["error"] == "tracking_not_found"
```

#### ✅ Shipments Listing Tests

```python
def test_list_shipments_by_status_success():
    """Verifica el listado exitoso de unidades por estado"""
    # Arrange: Crear unidades
    for i in range(3):
        self.client.post('/api/v1/checkpoints',
            json={
                "tracking_id": f"TEST{i:03d}",
                "status": "CREATED",
                "location": "Bogotá",
                "description": f"Unidad {i}",
                "timestamp": "2024-01-15T10:30:00Z"
            },
            headers={"X-API-Key": "test-api-key"}
        )
    
    # Act
    response = self.client.get('/api/v1/shipments?status=CREATED',
        headers={"X-API-Key": "test-api-key"}
    )
    
    # Assert
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert len(data["units"]) == 3
    assert all(unit["status"] == "CREATED" for unit in data["units"])
```

## 🛠️ Configuración de Pruebas

### Fixtures (conftest.py)

```python
@pytest.fixture
def app():
    """Aplicación Flask para pruebas"""
    app = create_app(testing=True)
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Cliente de pruebas Flask"""
    return app.test_client()

@pytest.fixture
def sample_checkpoint_data():
    """Datos de ejemplo para checkpoints"""
    return {
        "status": UnitStatus.PICKED_UP,
        "location": "Bogotá, Colombia",
        "description": "Paquete recogido",
        "timestamp": datetime.now()
    }
```

### Configuración pytest.ini

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --tb=short
    --strict-markers
    --disable-warnings
markers =
    unit: Pruebas unitarias
    integration: Pruebas de integración
    slow: Pruebas que tardan más tiempo
```

## 🚀 Ejecución de Pruebas

### Comandos de Pruebas

```bash
# Ejecutar todas las pruebas
docker-compose exec app python3 -m pytest

# Pruebas unitarias solamente
docker-compose exec app python3 -m pytest tests/unit/ -m unit

# Pruebas de integración solamente
docker-compose exec app python3 -m pytest tests/integration/ -m integration

# Pruebas con coverage
docker-compose exec app python3 -m pytest --cov=src --cov-report=html

# Pruebas específicas
docker-compose exec app python3 -m pytest tests/unit/test_domain_entities.py::test_unit_creation

# Pruebas con verbose output
docker-compose exec app python3 -m pytest -v

# Pruebas que fallan solamente
docker-compose exec app python3 -m pytest --lf
```

### Reportes de Cobertura

```bash
# Generar reporte HTML de cobertura
docker-compose exec app python3 -m pytest --cov=src --cov-report=html

# Ver cobertura en terminal
docker-compose exec app python3 -m pytest --cov=src --cov-report=term-missing
```
---
