from abc import ABC, abstractmethod
from typing import Dict, Any
from backend.src.models.simulation import SimulationSettings
import uuid

class ISimulationManager(ABC):
    @abstractmethod
    def start_simulation(self, settings: SimulationSettings) -> str:
        """Starts a new simulation and returns the job ID."""
        pass

    @abstractmethod
    def get_job_status(self, job_id: str) -> Dict[str, Any] | None:
        """Gets the status of a simulation job."""
        pass

class SimulationManager(ISimulationManager):
    """Manages the lifecycle of simulation jobs."""
    def __init__(self):
        self._jobs: Dict[str, Any] = {}
        # This class will later interact with physics and evolution services.
        
    def start_simulation(self, settings: SimulationSettings) -> str:
        job_id = str(uuid.uuid4())
        self._jobs[job_id] = {"status": "running", "settings": settings.model_dump()}
        return job_id

    def get_job_status(self, job_id: str) -> Dict[str, Any] | None:
        return self._jobs.get(job_id)
