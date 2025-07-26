from abc import ABC, abstractmethod
from backend.src.models.creature import Creature
from backend.src.models.simulation import SimulationSettings

class IPhysicsService(ABC):
    """Interface for a physics simulation service."""
    @abstractmethod
    def run_simulation(self, creature: Creature, settings: SimulationSettings) -> float:
        """
        Runs a physics simulation for a single creature and returns its fitness score.
        """
        pass
