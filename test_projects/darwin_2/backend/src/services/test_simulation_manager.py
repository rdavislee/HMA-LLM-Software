from backend.src.services.simulation_manager import SimulationManager
from backend.src.models.simulation import SimulationSettings

def test_start_simulation_returns_job_id():
    manager = SimulationManager()
    settings = SimulationSettings()
    job_id = manager.start_simulation(settings)
    assert isinstance(job_id, str)

def test_get_job_status_for_new_job():
    manager = SimulationManager()
    settings = SimulationSettings()
    job_id = manager.start_simulation(settings)
    status = manager.get_job_status(job_id)
    assert status is not None
    assert status["status"] == "running"

def test_get_status_for_nonexistent_job():
    manager = SimulationManager()
    status = manager.get_job_status("nonexistent-id")
    assert status is None
