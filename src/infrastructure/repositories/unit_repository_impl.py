from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from ...domain.entities.unit import Unit
from ...domain.value_objects.tracking_id import TrackingId
from ...domain.value_objects.unit_status import UnitStatus
from ...domain.value_objects.checkpoint_data import CheckpointData
from ...domain.repositories.unit_repository import UnitRepository
from ..database.database import db
from ..database.models import UnitModel, CheckpointModel


class UnitRepositoryImpl(UnitRepository):
    """Implementación del repositorio de Unit usando SQLAlchemy"""
    
    def __init__(self):
        self.db = db
    
    def _model_to_entity(self, model: UnitModel) -> Unit:
        """Convierte un modelo SQLAlchemy a entidad de dominio"""
        checkpoints = []
        for cp_model in model.checkpoints:
            checkpoint_data = CheckpointData(
                status=UnitStatus(cp_model.status),
                timestamp=cp_model.timestamp,
                location=cp_model.location,
                notes=cp_model.notes,
                operator_id=cp_model.operator_id
            )
            checkpoints.append(checkpoint_data)
        
        return Unit(
            id=model.id,
            tracking_id=TrackingId(model.tracking_id),
            current_status=UnitStatus(model.current_status),
            created_at=model.created_at,
            updated_at=model.updated_at,
            checkpoints=checkpoints
        )
    
    def _entity_to_model(self, entity: Unit) -> UnitModel:
        """Convierte una entidad de dominio a modelo SQLAlchemy"""
        from uuid import uuid4
        return UnitModel(
            id=entity.id or str(uuid4()),
            tracking_id=str(entity.tracking_id),
            current_status=entity.current_status.value,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )
    
    def save(self, unit: Unit) -> Unit:
        """Guarda una unidad en el repositorio"""
        try:
            # Buscar si ya existe
            existing_model = self.db.session.query(UnitModel).filter_by(
                tracking_id=str(unit.tracking_id)
            ).first()
            
            if existing_model:
                # Actualizar existente
                existing_model.current_status = unit.current_status.value
                existing_model.updated_at = unit.updated_at
                
                # Actualizar checkpoints
                self.db.session.query(CheckpointModel).filter_by(
                    unit_id=existing_model.id
                ).delete()
                
                for checkpoint_data in unit.checkpoints:
                    checkpoint_model = CheckpointModel(
                        id=None,  # Se generará automáticamente
                        tracking_id=str(unit.tracking_id),
                        status=checkpoint_data.status.value,
                        timestamp=checkpoint_data.timestamp,
                        location=checkpoint_data.location,
                        notes=checkpoint_data.notes,
                        operator_id=checkpoint_data.operator_id,
                        unit_id=existing_model.id
                    )
                    self.db.session.add(checkpoint_model)
                
                saved_model = existing_model
            else:
                # Crear nuevo
                unit_model = self._entity_to_model(unit)
                self.db.session.add(unit_model)
                self.db.session.flush()  # Para obtener el ID
                
                # Agregar checkpoints
                for checkpoint_data in unit.checkpoints:
                    checkpoint_model = CheckpointModel(
                        id=None,
                        tracking_id=str(unit.tracking_id),
                        status=checkpoint_data.status.value,
                        timestamp=checkpoint_data.timestamp,
                        location=checkpoint_data.location,
                        notes=checkpoint_data.notes,
                        operator_id=checkpoint_data.operator_id,
                        unit_id=unit_model.id
                    )
                    self.db.session.add(checkpoint_model)
                
                saved_model = unit_model
            
            self.db.session.commit()
            
            # Recargar con relaciones
            return self.find_by_id(saved_model.id)
        except Exception as e:
            self.db.session.rollback()
            raise e
    
    def find_by_tracking_id(self, tracking_id: TrackingId) -> Optional[Unit]:
        """Busca una unidad por su tracking ID"""
        model = self.db.session.query(UnitModel).filter_by(
            tracking_id=str(tracking_id)
        ).first()
        
        return self._model_to_entity(model) if model else None
    
    def find_by_id(self, unit_id: str) -> Optional[Unit]:
        """Busca una unidad por su ID"""
        model = self.db.session.query(UnitModel).filter_by(id=unit_id).first()
        
        return self._model_to_entity(model) if model else None
    
    def find_by_status(self, status: UnitStatus) -> List[Unit]:
        """Busca todas las unidades con un estado específico"""
        models = self.db.session.query(UnitModel).filter_by(
            current_status=status.value
        ).all()
        
        return [self._model_to_entity(model) for model in models]
    
    def find_all(self, limit: int = 100, offset: int = 0) -> List[Unit]:
        """Retorna todas las unidades con paginación"""
        models = self.db.session.query(UnitModel).offset(offset).limit(limit).all()
        
        return [self._model_to_entity(model) for model in models]
    
    def exists_by_tracking_id(self, tracking_id: TrackingId) -> bool:
        """Verifica si existe una unidad con el tracking ID dado"""
        count = self.db.session.query(UnitModel).filter_by(
            tracking_id=str(tracking_id)
        ).count()
        
        return count > 0
    
    def count_by_status(self, status: UnitStatus) -> int:
        """Cuenta el número de unidades con un estado específico"""
        return self.db.session.query(UnitModel).filter_by(
            current_status=status.value
        ).count()
    
    def delete(self, unit_id: str) -> bool:
        """Elimina una unidad del repositorio"""
        with self.db.session.begin():
            model = self.db.session.query(UnitModel).filter_by(id=unit_id).first()
            if model:
                self.db.session.delete(model)
                self.db.session.commit()
                return True
            return False
