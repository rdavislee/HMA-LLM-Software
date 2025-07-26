from backend.src.models.simulation import SimulationRequest, SimulationSettings

def test_create_simulation_settings():
    settings = SimulationSettings(
        population_size=100,
        generations=200,
        mutation_rate=0.05,
        gravity=-10.0
    )
    assert settings.population_size == 100
    assert settings.generations == 200
    assert settings.mutation_rate == 0.05
    assert settings.gravity == -10.0

def test_create_simulation_request():
    settings = SimulationSettings()
    request = SimulationRequest(settings=settings)
    assert request.settings.population_size == 50
