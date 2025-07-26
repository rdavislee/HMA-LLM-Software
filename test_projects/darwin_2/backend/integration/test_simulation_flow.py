from backend.src.models.creature import Brain, Creature
from backend.src.models.simulation import SimulationSettings
from backend.src.services.evolution_service import EvolutionService
from backend.src.services.physics_service import PhysicsService


def test_full_generation_flow():
    physics_service = PhysicsService()
    evolution_service = EvolutionService()
    settings = SimulationSettings(
        population_size=10, generations=1, mutation_rate=0.1, gravity=-9.8
    )
    initial_population = [
        Creature(id=i, nodes=[], muscles=[], brain=Brain(weights=[]))
        for i in range(settings.population_size)
    ]
    for creature in initial_population:
        creature.fitness = physics_service.simulate_creature(creature, settings)
    next_generation = evolution_service.evolve_population(initial_population, settings)
    assert len(next_generation) == settings.population_size
    assert all(isinstance(c, Creature) for c in next_generation)
