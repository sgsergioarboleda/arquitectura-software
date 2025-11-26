from pathlib import Path
import sys
from unittest.mock import MagicMock, patch

# Añadir la raíz del proyecto y el directorio backend al PYTHONPATH
project_root = Path(__file__).resolve().parents[2]  # ...\arquitectura-software-1
backend_root = Path(__file__).resolve().parents[1]  # ...\backend
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(backend_root))

# Parchear auth_service ANTES de importar main
# Esto evita que intente cargar las llaves RSA
with patch('Auth.auth_service.auth_service') as mock_auth:
    mock_auth.verify_token = MagicMock(return_value={"user_id": "test"})
    mock_auth.create_access_token = MagicMock(return_value="fake_token")
    
    from fastapi.testclient import TestClient
    from main import app

def test_health_endpoint_returns_healthy():
    """Prueba que el endpoint /health retorna estado healthy"""
    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("status") == "healthy"