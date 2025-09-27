#!/usr/bin/env python3
"""
Script simple para verificar que la estructura del proyecto está correcta
"""

import sys
import os

def test_imports():
    """Verifica que los imports principales funcionen"""
    try:
        # Agregar el directorio src al path
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        
        # Test imports de dominio
        from domain.value_objects.tracking_id import TrackingId
        from domain.value_objects.unit_status import UnitStatus
        from domain.value_objects.checkpoint_data import CheckpointData
        from domain.entities.unit import Unit
        from domain.entities.checkpoint import Checkpoint
        
        print("✅ Imports de dominio funcionan correctamente")
        
        # Test imports de aplicación
        from application.use_cases.register_checkpoint import RegisterCheckpointUseCase
        from application.use_cases.get_tracking_history import GetTrackingHistoryUseCase
        from application.use_cases.list_units_by_status import ListUnitsByStatusUseCase
        
        print("✅ Imports de aplicación funcionan correctamente")
        
        # Test imports de infraestructura
        from infrastructure.database.models import UnitModel, CheckpointModel
        from infrastructure.repositories.unit_repository_impl import UnitRepositoryImpl
        from infrastructure.repositories.checkpoint_repository_impl import CheckpointRepositoryImpl
        
        print("✅ Imports de infraestructura funcionan correctamente")
        
        # Test imports de presentación
        from presentation.controllers.checkpoint_controller import CheckpointController
        from presentation.schemas.checkpoint_schemas import RegisterCheckpointSchema
        
        print("✅ Imports de presentación funcionan correctamente")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error de import: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def test_domain_objects():
    """Verifica que los objetos de dominio funcionen"""
    try:
        from domain.value_objects.tracking_id import TrackingId
        from domain.value_objects.unit_status import UnitStatus
        from domain.value_objects.checkpoint_data import CheckpointData
        from domain.entities.unit import Unit
        from datetime import datetime
        
        # Test TrackingId
        tracking_id = TrackingId("TEST123")
        assert str(tracking_id) == "TEST123"
        print("✅ TrackingId funciona correctamente")
        
        # Test UnitStatus
        assert UnitStatus.is_valid_status("CREATED")
        assert not UnitStatus.is_valid_status("INVALID")
        print("✅ UnitStatus funciona correctamente")
        
        # Test CheckpointData
        checkpoint_data = CheckpointData(
            status=UnitStatus.CREATED,
            timestamp=datetime.utcnow()
        )
        assert checkpoint_data.status == UnitStatus.CREATED
        print("✅ CheckpointData funciona correctamente")
        
        # Test Unit
        unit = Unit.create(tracking_id)
        assert unit.tracking_id == tracking_id
        assert unit.current_status == UnitStatus.CREATED
        print("✅ Unit funciona correctamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en objetos de dominio: {e}")
        return False

def test_schemas():
    """Verifica que los schemas de validación funcionen"""
    try:
        from presentation.schemas.checkpoint_schemas import RegisterCheckpointSchema
        from marshmallow import ValidationError
        
        # Test schema válido
        valid_data = {
            'tracking_id': 'TEST123',
            'checkpoint_data': {
                'status': 'CREATED',
                'timestamp': '2024-01-01T10:00:00Z'
            }
        }
        
        schema = RegisterCheckpointSchema()
        result = schema.load(valid_data)
        assert result['tracking_id'] == 'TEST123'
        print("✅ Schema de validación funciona correctamente")
        
        # Test schema inválido
        invalid_data = {
            'tracking_id': 'AB',  # Muy corto
            'checkpoint_data': {
                'status': 'INVALID_STATUS'
            }
        }
        
        try:
            schema.load(invalid_data)
            print("❌ Schema debería haber fallado con datos inválidos")
            return False
        except ValidationError:
            print("✅ Schema valida correctamente datos inválidos")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en schemas: {e}")
        return False

def main():
    """Función principal"""
    print("🧪 Verificando estructura del proyecto...")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Objetos de Dominio", test_domain_objects),
        ("Schemas", test_schemas)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Ejecutando: {test_name}")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} falló")
    
    print("\n" + "=" * 50)
    print(f"📊 Resultados: {passed}/{total} tests pasaron")
    
    if passed == total:
        print("🎉 ¡Todos los tests pasaron! La estructura está correcta.")
        return 0
    else:
        print("⚠️  Algunos tests fallaron. Revisar la implementación.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

