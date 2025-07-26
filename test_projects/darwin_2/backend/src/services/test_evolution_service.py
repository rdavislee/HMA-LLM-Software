from backend.src.services.evolution_service import EvolutionService
from backend.src.models.creature import Creature, Brain


def test_evolve_population_mock():
    service = EvolutionService()
    population = [Creature(id=i, nodes=[], muscles=[], brain=Brain(weights=[])) for i in range(10)]
    next_gen = service.evolve_population(population, settings=None)
    assert len(next_gen) == len(population)
