import pytest
import json
from datetime import datetime

from src.domain.value_objects.tracking_id import TrackingId
from src.domain.value_objects.unit_status import UnitStatus


class TestCheckpointAPI:
    """Tests de integración para endpoints de checkpoints"""
    
    def test_register_checkpoint_success(self, client, auth_headers, sample_tracking_id, sample_checkpoint_data):
        """Test para registro exitoso de checkpoint"""
        # Simplemente crear un checkpoint PICKED_UP directamente (creará la unidad automáticamente)
        payload = {
            'tracking_id': sample_tracking_id,
            'checkpoint_data': sample_checkpoint_data
        }
        
        # Act
        response = client.post(
            '/api/v1/checkpoints',
            data=json.dumps(payload),
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 201
        data = response.get_json()
        assert 'checkpoint' in data
        assert 'unit' in data
        assert data['checkpoint']['tracking_id'] == sample_tracking_id
        assert data['checkpoint']['status'] == sample_checkpoint_data['status']
    
    def test_register_checkpoint_missing_api_key(self, client, sample_tracking_id, sample_checkpoint_data):
        """Test para error cuando falta API key"""
        # Arrange
        payload = {
            'tracking_id': sample_tracking_id,
            'checkpoint_data': sample_checkpoint_data
        }
        
        # Act
        response = client.post(
            '/api/v1/checkpoints',
            data=json.dumps(payload),
            headers={'Content-Type': 'application/json'}
        )
        
        # Assert
        assert response.status_code == 401
        data = response.get_json()
        assert data['error'] == 'invalid_api_key'
    
    def test_register_checkpoint_invalid_data(self, client, auth_headers):
        """Test para error con datos inválidos"""
        # Arrange
        payload = {
            'tracking_id': 'AB',  # Muy corto
            'checkpoint_data': {
                'status': 'INVALID_STATUS'
            }
        }
        
        # Act
        response = client.post(
            '/api/v1/checkpoints',
            data=json.dumps(payload),
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 400
        data = response.get_json()
        assert data['error'] == 'validation_error'
        assert 'details' in data
    
    def test_register_checkpoint_unit_not_found(self, client, auth_headers, sample_checkpoint_data):
        """Test para error cuando unidad no existe - ahora crea la unidad automáticamente"""
        # Arrange
        payload = {
            'tracking_id': 'NONEXISTENT123',
            'checkpoint_data': sample_checkpoint_data
        }
        
        # Act
        response = client.post(
            '/api/v1/checkpoints',
            data=json.dumps(payload),
            headers=auth_headers
        )
        
        # Assert - Ahora debería crear la unidad automáticamente
        assert response.status_code == 201
        data = response.get_json()
        assert 'checkpoint' in data
        assert 'unit' in data
    
    def test_get_tracking_history_success(self, client, auth_headers, sample_checkpoint_data):
        """Test para obtener historial exitosamente"""
        # Usar un tracking ID diferente para evitar conflictos
        tracking_id = 'HISTORY123456'
        # Primero crear un checkpoint (esto creará la unidad automáticamente)
        create_payload = {
            'tracking_id': tracking_id,
            'checkpoint_data': sample_checkpoint_data
        }
        
        create_response = client.post(
            '/api/v1/checkpoints',
            data=json.dumps(create_payload),
            headers=auth_headers
        )
        assert create_response.status_code == 201
        
        # Act - Obtener historial
        response = client.get(
            f'/api/v1/tracking/{tracking_id}',
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert 'unit' in data
        assert 'checkpoints' in data
        assert 'total_checkpoints' in data
        assert data['unit']['tracking_id'] == tracking_id
        assert len(data['checkpoints']) >= 1
    
    def test_get_tracking_history_not_found(self, client, auth_headers):
        """Test para error cuando tracking ID no existe"""
        # Act
        response = client.get(
            '/api/v1/tracking/NONEXISTENT456',
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 404
        data = response.get_json()
        assert data['error'] == 'business_error'
    
    def test_get_tracking_history_invalid_tracking_id(self, client, auth_headers):
        """Test para error con tracking ID inválido"""
        # Act
        response = client.get(
            '/api/v1/tracking/AB',  # Muy corto
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 400
        data = response.get_json()
        assert data['error'] == 'validation_error'
    
    def test_list_units_by_status_success(self, client, auth_headers):
        """Test para listar unidades por estado exitosamente"""
        # Act
        response = client.get(
            '/api/v1/shipments?status=CREATED',
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert 'units' in data
        assert 'pagination' in data
        assert 'status' in data
        assert data['status'] == 'CREATED'
        assert 'total' in data['pagination']
        assert 'limit' in data['pagination']
        assert 'offset' in data['pagination']
    
    def test_list_units_by_status_with_pagination(self, client, auth_headers):
        """Test para listar unidades con paginación"""
        # Act
        response = client.get(
            '/api/v1/shipments?status=CREATED&limit=10&offset=0',
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data['pagination']['limit'] == 10
        assert data['pagination']['offset'] == 0
    
    def test_list_units_by_status_invalid_status(self, client, auth_headers):
        """Test para error con estado inválido"""
        # Act
        response = client.get(
            '/api/v1/shipments?status=INVALID_STATUS',
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 400
        data = response.get_json()
        assert data['error'] == 'validation_error'
    
    def test_list_units_by_status_missing_status(self, client, auth_headers):
        """Test para error cuando falta estado"""
        # Act
        response = client.get(
            '/api/v1/shipments',
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 400
        data = response.get_json()
        assert data['error'] == 'validation_error'
    
    def test_health_check(self, client):
        """Test para endpoint de salud"""
        # Act
        response = client.get('/health')
        
        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert data['service'] == 'tracking-api'
    
    def test_404_error(self, client, auth_headers):
        """Test para endpoint no encontrado"""
        # Act
        response = client.get(
            '/api/v1/nonexistent',
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 404
        data = response.get_json()
        assert data['error'] == 'not_found'
    
    def test_method_not_allowed(self, client, auth_headers):
        """Test para método no permitido"""
        # Act
        response = client.delete(
            '/api/v1/checkpoints',
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 405
        data = response.get_json()
        assert data['error'] == 'method_not_allowed'
