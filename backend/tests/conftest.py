from pathlib import Path
import sys
from unittest.mock import MagicMock, patch
import pytest

# Añadir rutas al PYTHONPATH
project_root = Path(__file__).resolve().parents[2]
backend_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(backend_root))

# Parchear auth_service ANTES de cualquier import
sys.modules['Auth.auth_service'] = MagicMock()

@pytest.fixture(scope="session", autouse=True)
def setup_mocks():
    """Setup global mocks antes de importar main"""
    mock_auth_service = MagicMock()
    mock_auth_service.verify_token = MagicMock(return_value={"user_id": "test"})
    mock_auth_service.create_access_token = MagicMock(return_value="fake_token")
    
    sys.modules['Auth.auth_service'] = mock_auth_service
    sys.modules['Auth'] = MagicMock()
    
    yield

@pytest.fixture(autouse=True)
def mock_mongo_service(monkeypatch):
    """Mock mongo_service para evitar conexiones reales"""
    # Importar después de que conftest esté listo
    from main import mongo_service
    
    monkeypatch.setattr(mongo_service, "connect", lambda: True)
    monkeypatch.setattr(mongo_service, "is_connected", lambda: True)
    monkeypatch.setattr(mongo_service, "disconnect", lambda: None)
    # Remover la línea de "close" ya que el servicio no tiene ese método
    
    yield