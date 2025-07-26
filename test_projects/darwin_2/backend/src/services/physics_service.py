import pymunk
from backend.src.models.creature import Creature
from backend.src.models.simulation import SimulationSettings


class PhysicsService:
    def simulate_creature(
        self, creature: Creature, settings: SimulationSettings, duration: int = 10
    ) -> float:
        space = pymunk.Space()
        space.gravity = (0, settings.gravity)
        # Mock fitness result for now
        return float(creature.id * 10.0)
