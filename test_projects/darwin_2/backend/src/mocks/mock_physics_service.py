import random
from backend.src.services.i_physics_service import IPhysicsService
from backend.src.models.creature import Creature
from backend.src.models.simulation import SimulationSettings

class MockPhysicsService(IPhysicsService):
    """Mock implementation of the physics service for testing."""
    def run_simulation(self, creature: Creature, settings: SimulationSettings) -> float:
        """Returns a random fitness score."""
        return random.uniform(50.0, 500.0)
