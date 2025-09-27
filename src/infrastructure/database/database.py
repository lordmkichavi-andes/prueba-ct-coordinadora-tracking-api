from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

# Inicializar extensiones
db = SQLAlchemy()
migrate = Migrate()


def init_database(app):
    """Inicializa la base de datos con la aplicación Flask"""
    
    # Configurar base de datos
    database_url = os.getenv('DATABASE_URL', 'sqlite:///tracking.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Importar modelos para que SQLAlchemy los registre
    from .models import UnitModel, CheckpointModel, ShipmentModel, ShipmentUnitModel
    
    return db

