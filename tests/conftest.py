import pytest
import os
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import create_app
from src.infrastructure.database.database import db


@pytest.fixture(scope='session')
def app():
    """Fixture para la aplicación Flask de testing"""
    
    # Configurar base de datos de testing
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    os.environ['JWT_SECRET_KEY'] = 'test-secret-key'
    os.environ['API_KEY'] = 'test-api-key'
    
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Fixture para el cliente de testing"""
    return app.test_client()


@pytest.fixture
def db_session(app):
    """Fixture para la sesión de base de datos"""
    with app.app_context():
        yield db.session


@pytest.fixture
def auth_headers():
    """Fixture para headers de autenticación"""
    return {
        'X-API-Key': 'test-api-key',
        'Content-Type': 'application/json'
    }


@pytest.fixture
def sample_tracking_id():
    """Fixture para un tracking ID de prueba"""
    return "TEST123456"


@pytest.fixture
def sample_checkpoint_data():
    """Fixture para datos de checkpoint de prueba"""
    return {
        'status': 'PICKED_UP',
        'location': 'Centro de distribución',
        'notes': 'Paquete recogido exitosamente',
        'operator_id': 'OP001'
    }
