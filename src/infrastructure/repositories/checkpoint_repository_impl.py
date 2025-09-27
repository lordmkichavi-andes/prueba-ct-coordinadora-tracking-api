from typing import List, Optional
from sqlalchemy import desc

from ...domain.entities.checkpoint import Checkpoint
from ...domain.value_objects.tracking_id import TrackingId
from ...domain.value_objects.checkpoint_data import CheckpointData
from ...domain.repositories.checkpoint_repository import CheckpointRepository
from ..database.database import db
from ..database.models import CheckpointModel


class CheckpointRepositoryImpl(CheckpointRepository):
    """Implementación del repositorio de Checkpoint usando SQLAlchemy"""
    
    def __init__(self):
        self.db = db
    
    def _model_to_entity(self, model: CheckpointModel) -> Checkpoint:
        """Convierte un modelo SQLAlchemy a entidad de dominio"""
        from ...domain.value_objects.unit_status import UnitStatus
        
        checkpoint_data = CheckpointData(
            status=UnitStatus(model.status),
            timestamp=model.timestamp,
            location=model.location,
            notes=model.notes,
            operator_id=model.operator_id
        )
        
        return Checkpoint(
            id=model.id,
            tracking_id=TrackingId(model.tracking_id),
            checkpoint_data=checkpoint_data,
            created_at=model.created_at
        )
    
    def _entity_to_model(self, entity: Checkpoint) -> CheckpointModel:
        """Convierte una entidad de dominio a modelo SQLAlchemy"""
        from uuid import uuid4
        return CheckpointModel(
            id=entity.id or str(uuid4()),
            tracking_id=str(entity.tracking_id),
            status=entity.checkpoint_data.status.value,
            timestamp=entity.checkpoint_data.timestamp,
            location=entity.checkpoint_data.location,
            notes=entity.checkpoint_data.notes,
            operator_id=entity.checkpoint_data.operator_id
        )
    
    def save(self, checkpoint: Checkpoint) -> Checkpoint:
        """Guarda un checkpoint en el repositorio"""
        try:
            model = self._entity_to_model(checkpoint)
            # Asegurar que el ID esté presente
            if not model.id:
                from uuid import uuid4
                model.id = str(uuid4())
            self.db.session.add(model)
            self.db.session.commit()
            
            return self.find_by_id(model.id)
        except Exception as e:
            self.db.session.rollback()
            raise e
    
    def find_by_tracking_id(self, tracking_id: TrackingId) -> List[Checkpoint]:
        """Busca todos los checkpoints de una unidad por tracking ID"""
        models = self.db.session.query(CheckpointModel).filter_by(
            tracking_id=str(tracking_id)
        ).order_by(CheckpointModel.timestamp).all()
        
        return [self._model_to_entity(model) for model in models]
    
    def find_by_id(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """Busca un checkpoint por su ID"""
        model = self.db.session.query(CheckpointModel).filter_by(id=checkpoint_id).first()
        
        return self._model_to_entity(model) if model else None
    
    def find_latest_by_tracking_id(self, tracking_id: TrackingId) -> Optional[Checkpoint]:
        """Busca el último checkpoint de una unidad"""
        model = self.db.session.query(CheckpointModel).filter_by(
            tracking_id=str(tracking_id)
        ).order_by(desc(CheckpointModel.timestamp)).first()
        
        return self._model_to_entity(model) if model else None
    
    def find_all(self, limit: int = 100, offset: int = 0) -> List[Checkpoint]:
        """Retorna todos los checkpoints con paginación"""
        models = self.db.session.query(CheckpointModel).offset(offset).limit(limit).all()
        
        return [self._model_to_entity(model) for model in models]
    
    def count_by_tracking_id(self, tracking_id: TrackingId) -> int:
        """Cuenta el número de checkpoints de una unidad"""
        return self.db.session.query(CheckpointModel).filter_by(
            tracking_id=str(tracking_id)
        ).count()
    
    def delete(self, checkpoint_id: str) -> bool:
        """Elimina un checkpoint del repositorio"""
        with self.db.session.begin():
            model = self.db.session.query(CheckpointModel).filter_by(id=checkpoint_id).first()
            if model:
                self.db.session.delete(model)
                self.db.session.commit()
                return True
            return False
