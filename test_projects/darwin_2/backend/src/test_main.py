from fastapi.testclient import TestClient
from backend.src.main import app
from backend.src.core.container import app_state

def test_health_check():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

def test_startup_event_initializes_state():
    with TestClient(app) as client:
        assert hasattr(client.app.state, "app_state")
        assert client.app.state.app_state is app_state
        assert hasattr(client.app.state.app_state, "sim_manager")
