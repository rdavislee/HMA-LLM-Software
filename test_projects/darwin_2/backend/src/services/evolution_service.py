from typing import List
from backend.src.models.creature import Creature
from backend.src.models.simulation import SimulationSettings


class EvolutionService:
    def evolve_population(
        self, population: List[Creature], settings: SimulationSettings
    ) -> List[Creature]:
        # Mock implementation: just return the same population
        return population
