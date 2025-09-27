import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime

from src.domain.entities.unit import Unit
from src.domain.entities.checkpoint import Checkpoint
from src.domain.value_objects.tracking_id import TrackingId
from src.domain.value_objects.unit_status import UnitStatus
from src.domain.value_objects.checkpoint_data import CheckpointData
from src.application.use_cases.register_checkpoint import RegisterCheckpointUseCase
from src.application.use_cases.get_tracking_history import GetTrackingHistoryUseCase
from src.application.use_cases.list_units_by_status import ListUnitsByStatusUseCase


class TestRegisterCheckpointUseCase:
    """Tests para el caso de uso RegisterCheckpointUseCase"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.unit_repository = Mock()
        self.checkpoint_repository = Mock()
        self.unit_service = Mock()
        
        self.use_case = RegisterCheckpointUseCase(
            unit_repository=self.unit_repository,
            checkpoint_repository=self.checkpoint_repository,
            unit_service=self.unit_service
        )
    
    def test_register_checkpoint_success(self):
        """Test para registro exitoso de checkpoint"""
        # Arrange
        tracking_id = TrackingId("TEST123")
        checkpoint_data = CheckpointData(
            status=UnitStatus.PICKED_UP,
            timestamp=datetime.utcnow()
        )
        
        unit = Unit.create(tracking_id)
        checkpoint = Checkpoint.create(tracking_id, checkpoint_data)
        
        self.unit_repository.find_by_tracking_id.return_value = unit
        self.unit_service.add_checkpoint.return_value = unit
        self.unit_repository.save.return_value = unit
        self.checkpoint_repository.save.return_value = checkpoint
        
        # Act
        result = self.use_case.execute(tracking_id, checkpoint_data)
        
        # Assert
        assert 'checkpoint' in result
        assert 'unit' in result
        self.unit_repository.find_by_tracking_id.assert_called_once_with(tracking_id)
        self.unit_service.add_checkpoint.assert_called_once_with(tracking_id, checkpoint_data)
        self.unit_repository.save.assert_called_once_with(unit)
        self.checkpoint_repository.save.assert_called_once()
    
    def test_register_checkpoint_unit_not_found(self):
        """Test para crear unidad automáticamente cuando no existe"""
        # Arrange
        tracking_id = TrackingId("TEST123")
        checkpoint_data = CheckpointData(
            status=UnitStatus.PICKED_UP,
            timestamp=datetime.utcnow()
        )
        
        self.unit_repository.find_by_tracking_id.return_value = None
        
        # Mock para la unidad creada
        created_unit = Unit(
            id="test-id",
            tracking_id=tracking_id,
            current_status=UnitStatus.CREATED,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            checkpoints=[]
        )
        self.unit_repository.save.return_value = created_unit
        
        # Mock para el checkpoint creado
        created_checkpoint = Checkpoint(
            id="checkpoint-id",
            tracking_id=tracking_id,
            checkpoint_data=checkpoint_data,
            created_at=datetime.utcnow()
        )
        self.checkpoint_repository.save.return_value = created_checkpoint
        
        # Act
        result = self.use_case.execute(tracking_id, checkpoint_data)
        
        # Assert - Debería crear la unidad automáticamente
        assert result is not None
        # save se llama 2 veces: una para crear la unidad y otra para guardar después de agregar checkpoint
        assert self.unit_repository.save.call_count == 2
        self.checkpoint_repository.save.assert_called_once()
    
    def test_register_checkpoint_invalid_transition(self):
        """Test para error en transición inválida"""
        # Arrange
        tracking_id = TrackingId("TEST123")
        checkpoint_data = CheckpointData(
            status=UnitStatus.DELIVERED,  # Transición inválida desde CREATED
            timestamp=datetime.utcnow()
        )
        
        unit = Unit.create(tracking_id)
        self.unit_repository.find_by_tracking_id.return_value = unit
        self.unit_service.add_checkpoint.side_effect = ValueError("Transición inválida")
        
        # Act & Assert
        with pytest.raises(ValueError, match="Transición inválida"):
            self.use_case.execute(tracking_id, checkpoint_data)


class TestGetTrackingHistoryUseCase:
    """Tests para el caso de uso GetTrackingHistoryUseCase"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.unit_repository = Mock()
        self.checkpoint_repository = Mock()
        
        self.use_case = GetTrackingHistoryUseCase(
            unit_repository=self.unit_repository,
            checkpoint_repository=self.checkpoint_repository
        )
    
    def test_get_tracking_history_success(self):
        """Test para obtener historial exitosamente"""
        # Arrange
        tracking_id = TrackingId("TEST123")
        unit = Unit.create(tracking_id)
        
        checkpoint1 = Checkpoint.create(tracking_id, CheckpointData(
            status=UnitStatus.CREATED,
            timestamp=datetime.utcnow()
        ))
        
        checkpoint2 = Checkpoint.create(tracking_id, CheckpointData(
            status=UnitStatus.PICKED_UP,
            timestamp=datetime.utcnow()
        ))
        
        self.unit_repository.find_by_tracking_id.return_value = unit
        self.checkpoint_repository.find_by_tracking_id.return_value = [checkpoint1, checkpoint2]
        
        # Act
        result = self.use_case.execute(tracking_id)
        
        # Assert
        assert 'unit' in result
        assert 'checkpoints' in result
        assert 'total_checkpoints' in result
        assert result['total_checkpoints'] == 2
        self.unit_repository.find_by_tracking_id.assert_called_once_with(tracking_id)
        self.checkpoint_repository.find_by_tracking_id.assert_called_once_with(tracking_id)
    
    def test_get_tracking_history_unit_not_found(self):
        """Test para error cuando unidad no existe"""
        # Arrange
        tracking_id = TrackingId("TEST123")
        self.unit_repository.find_by_tracking_id.return_value = None
        
        # Act & Assert
        with pytest.raises(ValueError, match="Unidad con tracking ID TEST123 no encontrada"):
            self.use_case.execute(tracking_id)


class TestListUnitsByStatusUseCase:
    """Tests para el caso de uso ListUnitsByStatusUseCase"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.unit_repository = Mock()
        self.use_case = ListUnitsByStatusUseCase(unit_repository=self.unit_repository)
    
    def test_list_units_by_status_success(self):
        """Test para listar unidades por estado exitosamente"""
        # Arrange
        status = UnitStatus.PICKED_UP
        unit1 = Unit.create(TrackingId("TEST123"))
        unit2 = Unit.create(TrackingId("TEST456"))
        
        self.unit_repository.find_by_status.return_value = [unit1, unit2]
        
        # Act
        result = self.use_case.execute(status, limit=10, offset=0)
        
        # Assert
        assert 'units' in result
        assert 'pagination' in result
        assert 'status' in result
        assert len(result['units']) == 2
        assert result['status'] == status.value
        assert result['pagination']['total'] == 2
        self.unit_repository.find_by_status.assert_called_once_with(status)
    
    def test_list_units_by_status_with_pagination(self):
        """Test para listar unidades con paginación"""
        # Arrange
        status = UnitStatus.PICKED_UP
        units = [Unit.create(TrackingId(f"TEST{i}")) for i in range(5)]
        
        self.unit_repository.find_by_status.return_value = units
        
        # Act
        result = self.use_case.execute(status, limit=2, offset=1)
        
        # Assert
        assert len(result['units']) == 2
        assert result['pagination']['limit'] == 2
        assert result['pagination']['offset'] == 1
        assert result['pagination']['has_more'] is True
    
    def test_list_units_by_status_invalid_limit(self):
        """Test para límite inválido"""
        # Arrange
        status = UnitStatus.PICKED_UP
        self.unit_repository.find_by_status.return_value = []
        
        # Act
        result = self.use_case.execute(status, limit=0, offset=0)
        
        # Assert
        assert result['pagination']['limit'] == 100  # Valor por defecto
    
    def test_list_units_by_status_invalid_offset(self):
        """Test para offset inválido"""
        # Arrange
        status = UnitStatus.PICKED_UP
        self.unit_repository.find_by_status.return_value = []
        
        # Act
        result = self.use_case.execute(status, limit=10, offset=-1)
        
        # Assert
        assert result['pagination']['offset'] == 0  # Valor por defecto
