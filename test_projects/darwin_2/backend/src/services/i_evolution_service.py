from abc import ABC, abstractmethod
from typing import List, Tuple
from backend.src.models.creature import Creature

class IEvolutionService(ABC):
    """Interface for an evolutionary algorithm service."""
    @abstractmethod
    def generate_new_population(self, ranked_creatures: List[Tuple[Creature, float]], population_size: int) -> List[Creature]:
        """
        Takes a list of creatures ranked by fitness and generates a new population.
        """
        pass
