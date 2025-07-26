from fastapi.testclient import TestClient
from typing import Dict, Any
import uuid
from backend.src.main import app
from backend.src.api.dependencies import get_simulation_manager
from backend.src.services.simulation_manager import ISimulationManager

class MockSimulationManager(ISimulationManager):
    def __init__(self):
        self.jobs: Dict[str, Any] = {}
    def start_simulation(self, settings) -> str:
        job_id = str(uuid.uuid4())
        self.jobs[job_id] = {"status": "running", "settings": settings.model_dump()}
        return job_id
    def get_job_status(self, job_id: str) -> Dict[str, Any] | None:
        return self.jobs.get(job_id)

# Create a single, shared instance of the mock manager for the test suite.
# This ensures that state is preserved across different API calls within a single test.
mock_manager_instance = MockSimulationManager()

def get_mock_manager():
    """Dependency override that returns the singleton mock manager instance."""
    return mock_manager_instance

# Override the dependency for all tests in this file/app instance.
app.dependency_overrides[get_simulation_manager] = get_mock_manager

def test_start_and_get_simulation_status():
    """Tests the full flow of starting a simulation and then checking its status."""
    with TestClient(app) as client:
        # Ensure test isolation by clearing state from previous runs
        mock_manager_instance.jobs.clear()

        payload = {"settings": {"population_size": 50, "generations": 100, "mutation_rate": 0.05, "gravity": -9.81}}
        start_response = client.post("/api/v1/simulation/start", json=payload)
        assert start_response.status_code == 202
        job_id = start_response.json()["job_id"]
        
        # The mock manager instance is the same, so the job should be found.
        status_response = client.get(f"/api/v1/simulation/{job_id}/status")
        assert status_response.status_code == 200
        status_data = status_response.json()
        assert status_data["job_id"] == job_id
        assert status_data["status"] == "running"

def test_get_status_for_nonexistent_job():
    """Tests that a 404 is returned for a job that does not exist."""
    with TestClient(app) as client:
        response = client.get("/api/v1/simulation/nonexistent-job-id/status")
        assert response.status_code == 404
        assert response.json() == {"detail": "Job not found"}
