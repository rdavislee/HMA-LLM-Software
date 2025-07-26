from typing import List, Tuple
from backend.src.services.i_evolution_service import IEvolutionService
from backend.src.models.creature import Creature

class MockEvolutionService(IEvolutionService):
    """Mock implementation of the evolution service for testing."""
    def generate_new_population(self, ranked_creatures: List[Tuple[Creature, float]], population_size: int) -> List[Creature]:
        """Returns the top creatures to simulate a new generation."""
        top_creatures = [creature for creature, score in ranked_creatures]
        if not top_creatures:
            return []
        new_population = (top_creatures * (population_size // len(top_creatures) + 1))[:population_size]
        return new_population
