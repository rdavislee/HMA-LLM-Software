from backend.src.services.physics_service import PhysicsService
from backend.src.models.creature import Creature, Brain
from backend.src.models.simulation import SimulationSettings


def test_simulate_creature_mock():
    service = PhysicsService()
    creature = Creature(id=1, nodes=[], muscles=[], brain=Brain(weights=[]))
    settings = SimulationSettings(population_size=1, generations=1, mutation_rate=0.1)
    fitness = service.simulate_creature(creature, settings)
    assert isinstance(fitness, float)
