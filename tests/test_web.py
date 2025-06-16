import pytest
from flask import Flask
from pathlib import Path

from compiler.web import create_app

@pytest.fixture
def app(test_config_path: Path) -> Flask:
    """Create a test Flask application."""
    app = create_app(str(test_config_path))
    app.config.update({
        "TESTING": True,
    })
    return app
    
@pytest.fixture
def client(app: Flask):
    """Create a test client."""
    return app.test_client()
    
def test_index(client):
    """Test the index page."""
    response = client.get("/")
    assert response.status_code == 200
    
def test_compile_success(client):
    """Test successful compilation."""
    response = client.post("/api/compile", json={
        "code": """
        int main() {
            return 0;
        }
        """
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"]
    assert "result" in data
    
def test_compile_error(client):
    """Test compilation error handling."""
    response = client.post("/api/compile", json={
        "code": """
        int main() {
            return x;  // Undefined variable
        }
        """
    })
    assert response.status_code == 400
    data = response.get_json()
    assert not data["success"]
    assert "error" in data
    
def test_get_config(client):
    """Test getting configuration."""
    response = client.get("/api/config")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"]
    assert "config" in data
    
def test_update_config(client):
    """Test updating configuration."""
    response = client.post("/api/config", json={
        "compilation": {
            "optimization_level": 3
        }
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"]
    
def test_get_plugins(client):
    """Test getting plugin information."""
    response = client.get("/api/plugins")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"]
    assert "plugins" in data
    
def test_enable_plugin(client):
    """Test enabling a plugin."""
    response = client.post("/api/plugins/preprocessor/enable")
    assert response.status_code in (200, 400)  # 400 if plugin not found
    
def test_disable_plugin(client):
    """Test disabling a plugin."""
    response = client.post("/api/plugins/preprocessor/disable")
    assert response.status_code in (200, 400)  # 400 if plugin not found 