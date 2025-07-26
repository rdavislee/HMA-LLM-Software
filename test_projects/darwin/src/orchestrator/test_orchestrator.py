import numpy as np
import pytest
from unittest.mock import MagicMock, patch

# Assuming run_simulation is a method of an Orchestrator class
# and Orchestrator is imported from src.orchestrator.orchestrator
from src.orchestrator.orchestrator import run_simulation

# --- Test Partitions ---
# - Basic Flow: Verify the main loop runs correctly for a given number of generations.
# - Mock Interaction: Ensure that PhysicsEngine.simulate_creature, evolve_population, and generate_initial_population
#   are called with the correct arguments and frequency.
# - Fitness Assignment: Check if the fitness score returned by simulate_creature is correctly assigned to the creature.
# - Return Value: Verify the structure and content of the final returned best creature.
# - Edge Cases: Small number of creatures in population, zero generations.

# Dummy Creature class for testing purposes
class MockCreature:
    def __init__(self, genome=None, fitness=0.0, neural_network=None, *args, **kwargs):
        self.genome = genome
        self.fitness = fitness
        self.neural_network = neural_network # Add this line
        self.joints = []
        self.muscles = []
        self.initial_positions = []
        self.muscle_connectivity = []

    def __repr__(self):
        return f"MockCreature(genome={self.genome}, fitness={self.fitness})"

    def __eq__(self, other):
        if not isinstance(other, MockCreature):
            return NotImplemented
        return self.genome == other.genome and self.fitness == other.fitness

    def __lt__(self, other):
        return self.fitness < other.fitness

@pytest.fixture
def mock_orchestrator(mocker):
    '''Fixture to provide mocks for dependencies of run_simulation.'''
    # Mock module-level imports within src.orchestrator.orchestrator
    simulate_creature_mock = mocker.patch('src.orchestrator.orchestrator.simulate_creature')
    network_mock = mocker.patch('src.orchestrator.orchestrator.Network')
    evolve_population_mock = mocker.patch('src.orchestrator.orchestrator.evolve_population')
    creature_class_mock = mocker.patch('src.orchestrator.orchestrator.Creature')
    
    # Patch specific random functions directly
    randint_mock = mocker.patch('src.orchestrator.orchestrator.random.randint')
    choice_mock = mocker.patch('src.orchestrator.orchestrator.random.choice')
    sample_mock = mocker.patch('src.orchestrator.orchestrator.random.sample')

    randint_mock.return_value = 5 # This ensures num_joints is 5 for initial population
    choice_mock.side_effect = lambda seq: list(seq)[0] # Ensure random.choice always returns an element from the provided sequence
    sample_mock.return_value = [0, 1] # Mock random.sample for muscle connectivity
    
    np_random_uniform_mock = mocker.patch('src.orchestrator.orchestrator.np.random.uniform')
    np_random_uniform_mock.return_value = np.array([[1.0, 1.0], [2.0, 2.0], [3.0, 3.0], [4.0, 4.0], [5.0, 5.0]])

    # Configure mock instances/return values
    # Initial positions must be lists, not numpy arrays
    simulate_creature_mock.return_value = ("dummy_playback_data", 10.0, [[0.0, 0.0], [1.0, 1.0]], [[0, 1]])

    evolve_population_mock.side_effect = lambda pop, settings: [
        MockCreature(genome=f"evolved_creature_genome_{i}") for i in range(len(pop))
    ]

    # When Creature() is called in orchestrator.py, return our MockCreature
    creature_class_mock.side_effect = MockCreature

    yield (
        simulate_creature_mock,
        network_mock,
        evolve_population_mock,
        creature_class_mock,
        randint_mock,
        choice_mock,
        sample_mock,
        np_random_uniform_mock
    )



@pytest.fixture
def network_mock(mock_orchestrator):
    return mock_orchestrator[1]

@pytest.fixture
def evolve_population_mock(mock_orchestrator):
    return mock_orchestrator[2]



@pytest.fixture
def creature_class_mock(mock_orchestrator):
    return mock_orchestrator[3]
@pytest.fixture
def simulate_creature_mock(mock_orchestrator):
    return mock_orchestrator[0]



@pytest.fixture
def np_random_uniform_mock(mock_orchestrator):
    return mock_orchestrator[5]

@pytest.fixture
def simulation_settings():
    '''Fixture for standard simulation settings.'''
    return {
        "minSpringRest": 50, "maxSpringRest": 150, "minInitialSpringLength": 30,
        "maxInitialSpringLength": 70, "groundFriction": 0.5, "jointWeight": 1.0,
        "minJoints": 3, "maxJoints": 8, "springStiffness": 100,
        "nnWeightMutationChance": 10, "jointPositionMutationChance": 5,
        "addRemoveJointMutationChance": 2, "addRemoveMuscleMutationChance": 5
    }

# Test suite for run_simulation
class TestRunSimulation:

    # Covers: Basic Flow, Mock Interaction (call counts for generations and creatures)
    def test_run_simulation_flow_and_call_counts(self, simulation_settings, simulate_creature_mock, evolve_population_mock, creature_class_mock):
        generations = 3
        initial_population_size = 100 # Assuming run_simulation creates this many initial creatures

        # Run the simulation
        run_simulation(simulation_settings, generations)

        # Verify correct number of generations are run
        # simulate_creature is called for each creature in each generation
        expected_simulate_calls = generations * initial_population_size
        assert simulate_creature_mock.call_count == expected_simulate_calls, (
            f"Expected simulate_creature to be called {expected_simulate_calls} times, but got {simulate_creature_mock.call_count}"
        )

        # evolve_population is called after each generation, except the last one
        expected_evolve_calls = generations - 1
        assert evolve_population_mock.call_count == expected_evolve_calls, (
            f"Expected evolve_population to be called {expected_evolve_calls} times, but got {evolve_population_mock.call_count}"
        )
        
        # Verify Creature class was called to generate initial population
        assert creature_class_mock.call_count == initial_population_size, (
            f"Expected Creature() to be called exactly {initial_population_size} times for initial population."
        )

    # Covers: Fitness Assignment
    def test_fitness_is_correctly_assigned(self, simulation_settings, simulate_creature_mock, creature_class_mock, evolve_population_mock):
        generations = 1 # Test with a single generation to simplify
        
        initial_creatures_generated_by_run_simulation = [MockCreature(genome=f"creature_{i}") for i in range(100)]
        creature_class_mock.side_effect = initial_creatures_generated_by_run_simulation

        mock_fitness_values = [float(i + 1) for i in range(100)] # Simple increasing fitness
        simulate_creature_mock.side_effect = [
            (f"playback_{i}", mock_fitness_values[i], [[0.0, 0.0], [1.0, 1.0]], [[0, 1]]) for i in range(100)
        ]

        # Run the simulation
        run_simulation(simulation_settings, generations)

        # Assert that evolve_population was called correctly with creatures and their assigned fitnesses
        # It should be called once for generations = 1.
        evolve_population_mock.assert_not_called()
        


    # Covers: Return Value (best creature of final generation)
    def test_returns_best_creature_of_final_generation(self, simulation_settings, simulate_creature_mock, evolve_population_mock, creature_class_mock):
        generations = 2
        
        # Generation 0 creatures - these are created by run_simulation calling Creature()
        # So we configure creature_class_mock.side_effect to return these
        initial_population_size = 100
        gen0_creatures_for_mock = [MockCreature(genome=f"gen0_creature_{i}") for i in range(initial_population_size)]
        creature_class_mock.side_effect = gen0_creatures_for_mock

        # Simulate creature side effects for Generation 0 and Generation 1
        # PhysicsEngine.simulate_creature will be called for each creature in each generation
        # We need 100 results for gen0 and 100 results for gen1.
        # Let's make the last creature of the final generation the best.
        # Simulate creature side effects for Generation 0 and Generation 1
        # PhysicsEngine.simulate_creature will be called for each creature in each generation
        # We need 100 results for gen0 and 100 results for gen1.
        # Let's make the last creature of the final generation the best.
        gen0_sim_results = [(f"pb_gen0_{i}", i + 1.0, [[0.0, 0.0], [1.0, 1.0]], [[0, 1]]) for i in range(initial_population_size)]
        gen1_sim_results = [(f"pb_gen1_{i}", initial_population_size + i + 1.0, [[0.0, 0.0], [1.0, 1.0]], [[0, 1]]) for i in range(initial_population_size)]
        
        # Manually set a higher fitness for the "best" creature in the final generation
        # and provide specific playback data, initial positions, and muscle connectivity for it
        expected_best_playback_data = "pb_gen1_99_best_data"
        expected_best_fitness_score = 1000.0
        expected_best_initial_positions = [[99.0, 99.0], [100.0, 100.0]] # Must be list of lists
        expected_best_muscle_connectivity = [[0, 1], [1, 2], [0, 2]] # Example distinct connectivity

        gen1_sim_results[-1] = (
            expected_best_playback_data,
            expected_best_fitness_score,
            expected_best_initial_positions,
            expected_best_muscle_connectivity
        )

        simulate_creature_mock.side_effect = gen0_sim_results + gen1_sim_results

        # Evolve population side effect for Generation 0 -> Generation 1
        gen1_creatures = [MockCreature(genome=f"gen1_creature_{i}") for i in range(initial_population_size)]
        # Ensure evolve_population returns these specific creatures for the next generation
        evolve_population_mock.return_value = gen1_creatures

        # Run the simulation
        result = run_simulation(simulation_settings, generations)

        # Verify the returned best creature data structure and values
        assert "playbackData" in result
        assert "fitnessScores" in result
        assert "initialPositions" in result
        assert "muscleConnectivity" in result

        # Check that the lists contain all creatures from the final generation
        assert len(result["playbackData"]) == initial_population_size
        assert len(result["fitnessScores"]) == initial_population_size
        assert len(result["initialPositions"]) == initial_population_size
        assert len(result["muscleConnectivity"]) == initial_population_size

        # Check that the best creature's data is at the first position after sorting
        assert result["playbackData"][0] == expected_best_playback_data
        assert result["fitnessScores"][0] == expected_best_fitness_score
        assert result["initialPositions"][0] == expected_best_initial_positions
        assert result["muscleConnectivity"][0] == expected_best_muscle_connectivity



    # Covers: Edge case - zero generations
    # This test assumes that `run_simulation` should raise a ValueError for 0 generations.
    # Adjust assertion if the actual implementation handles 0 generations differently (e.g., returns empty/default).
    def test_run_simulation_zero_generations(self, simulation_settings, simulate_creature_mock, evolve_population_mock, creature_class_mock):
        generations = 0

        with pytest.raises(ValueError, match="Generations must be a positive integer"):
             run_simulation(simulation_settings, generations)

        # Verify no simulation or evolution calls were made
        assert simulate_creature_mock.call_count == 0
        assert evolve_population_mock.call_count == 0
        assert creature_class_mock.call_count == 0 # No initial population generated