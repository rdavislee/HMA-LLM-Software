import pytest
import numpy as np
import random
from unittest.mock import MagicMock, patch

class DynamicSideEffect:
    def __init__(self, values):
        self.values = iter(values)

    def __call__(self, *args, **kwargs):
        next_value = next(self.values)
        # Only call next_value if it's a lambda specifically intended to process random.choice arguments.
        # Otherwise, return it directly, letting the mocked code handle calling if it's a function object.
        if callable(next_value) and getattr(next_value, '__name__', None) == '<lambda>':
            return next_value(*args, **kwargs)
        return next_value

from src.evolution.genetic_algorithm import evolve_population, _add_remove_muscle, _add_remove_joint
from src.creature.creature import Creature
from src.creature.models.joint import Joint
from src.creature.models.muscle import Muscle

class MockNeuralNetwork:
    def __init__(self, input_size, output_size, hidden_layers, weights=None, biases=None):
        self.input_size = input_size
        self.output_size = output_size
        self.hidden_layers = hidden_layers
        
        target_output_dim = output_size if output_size > 0 else 0 

        if weights is not None:
            self.weights = weights
        else:
            self.weights = []
            if not hidden_layers: # Direct connection
                if target_output_dim > 0:
                    self.weights.append(np.random.rand(input_size, target_output_dim))
            else:
                self.weights.append(np.random.rand(input_size, hidden_layers[0]))
                for i in range(len(hidden_layers) - 1):
                    self.weights.append(np.random.rand(hidden_layers[i], hidden_layers[i+1]))
                if target_output_dim > 0:
                    self.weights.append(np.random.rand(hidden_layers[-1], target_output_dim))

        if biases is not None:
            self.biases = biases
        else:
            self.biases = []
            if not hidden_layers: # No hidden layers, only output layer biases
                if target_output_dim > 0:
                    self.biases.append(np.random.rand(target_output_dim))
            else:
                self.biases.append(np.random.rand(hidden_layers[0]))
                for i in range(len(hidden_layers) - 1):
                    self.biases.append(np.random.rand(hidden_layers[i+1]))
                if target_output_dim > 0:
                    self.biases.append(np.random.rand(target_output_dim))

    def predict(self, inputs):
        if self.output_size == 0:
            return np.array([])
        return np.random.rand(self.output_size)

    def get_weights(self):
        return self.weights

    def get_biases(self):
        return self.biases

    def set_weights(self, new_weights):
        self.weights = new_weights

    def set_biases(self, new_biases):
        self.biases = new_biases

    def clone(self):
        return MockNeuralNetwork(
            self.input_size,
            self.output_size,
            self.hidden_layers,
            weights=[w.copy() for w in self.weights],
            biases=[b.copy() for b in self.biases]
        )
    def update_input_topology(self, new_input_size: int):
        # Mock implementation: just update the input_size and pass
        self.input_size = new_input_size
        pass

    def update_output_topology(self, new_output_size: int):
        # Mock implementation: just update the output_size and pass
        self.output_size = new_output_size
        pass

def create_mock_creature_class():
    class MockCreatureWithID:
        _next_id = 0
        
        def __init__(self, *args, **kwargs):
            # Store the explicit ID if provided, otherwise generate one.
            if 'id' in kwargs:
                self.id = kwargs['id']
            else:
                self.id = f"mock_creature_{MockCreatureWithID._next_id}"
                MockCreatureWithID._next_id += 1
            
            self.fitness = kwargs.get('fitness', 0)
            self.parent_id = kwargs.get('parent_id')
            self.neural_network = kwargs.get('neural_network', MockNeuralNetwork(1, 1, []))
            
            num_joints_initial = kwargs.get('num_joints', 4) 
            num_muscles_initial = kwargs.get('num_muscles', 2) 
            self.joints = kwargs.get('joints', [MagicMock(spec=Joint) for _ in range(num_joints_initial)])
            self.muscles = kwargs.get('muscles', [MagicMock(spec=Muscle, joint1_idx=i, joint2_idx=(i+1)%num_joints_initial if num_joints_initial > 1 else 0) for i in range(num_muscles_initial)])

            # Mock methods that evolve_population expects
            self.get_joint_positions = MagicMock(return_value=np.array([0,0]))
            self.get_muscle_connectivity = MagicMock(return_value=[])
            self.update_topology_from_muscles = MagicMock()
            self.update_input_output_topology = MagicMock()

        def clone(self):
            cloned_nn = self.neural_network.clone()
            child = MockCreatureWithID(
                parent_id=self.id, 
                neural_network=cloned_nn, 
                joints=list(self.joints), 
                muscles=list(self.muscles)
            )
            return child

        @property
        def num_joints(self):
            return len(self.joints)

        def add_joint(self, position: np.ndarray, index: int = None):
            new_joint = MagicMock(spec=Joint, position=position)
            if index is None or index >= len(self.joints):
                self.joints.append(new_joint)
            else:
                self.joints.insert(index, new_joint)
            if hasattr(self.neural_network, 'update_input_topology'):
                 self.neural_network.update_input_topology(self.num_joints * 4 + self.num_muscles * 2)

        def remove_joint(self, index: int):
            if 0 <= index < len(self.joints):
                removed_joint = self.joints.pop(index)
                if hasattr(self.neural_network, 'update_input_topology'):
                     self.neural_network.update_input_topology(self.num_joints * 4 + self.num_muscles * 2)
                return removed_joint
            else:
                raise IndexError("Joint index out of bounds")

        @property
        def num_muscles(self):
            return len(self.muscles)

        def add_muscle(self, muscle):
            self.muscles.append(muscle)
            if hasattr(self.neural_network, 'update_input_topology'):
                 self.neural_network.update_input_topology(self.num_joints * 4 + self.num_muscles * 2)
            if hasattr(self.neural_network, 'update_output_topology'):
                self.neural_network.update_output_topology(self.num_muscles)

        def remove_muscle(self, index):
            if 0 <= index < len(self.muscles):
                removed_muscle = self.muscles.pop(index)
                if hasattr(self.neural_network, 'update_input_topology'):
                     self.neural_network.update_input_topology(self.num_joints * 4 + self.num_muscles * 2)
                if hasattr(self.neural_network, 'update_output_topology'):
                    self.neural_network.update_output_topology(self.num_muscles)
                return removed_muscle
            else:
                raise IndexError("Muscle index out of bounds")
    
    return MockCreatureWithID

def create_dummy_creature(num_joints=3, num_muscles=2, fixed_seed=None, hidden_layers=[4]):
    if fixed_seed is not None:
        random.seed(fixed_seed)
        np.random.seed(fixed_seed)

    joints = []
    for i in range(num_joints):
        joints.append(Joint(x=random.uniform(0, 100), y=random.uniform(0, 100), mass=1.0))

    muscles = []
    for _ in range(num_muscles):
        j1_idx = random.randint(0, num_joints - 1)
        j2_idx = random.randint(0, num_joints - 1)
        while j1_idx == j2_idx:
            j2_idx = random.randint(0, num_joints - 1)
        
        muscles.append(Muscle(joint1_idx=min(j1_idx, j2_idx), joint2_idx=max(j1_idx, j2_idx), initial_length=50, stiffness=100, damping_coefficient=0.1))
    
    calculated_input_size = (len(joints) * 4) + (len(muscles) * 2)
    nn = MockNeuralNetwork(input_size=calculated_input_size, output_size=num_muscles, hidden_layers=hidden_layers)
    
    creature = Creature(joints, muscles, nn)
 
    return creature

class TestEvolvePopulation:

    @pytest.fixture
    def default_settings(self):
        return {
            "population_size": 10,
            "elitism_count": 2,
            "mutation_rate": 0.1,
            "nnWeightMutationChance": 50,
            "jointPositionMutationChance": 50,
            "addRemoveJointMutationChance": 50,
            "addRemoveMuscleMutationChance": 50,
            "minJoints": 3,
            "maxJoints": 8,
            "minMuscles": 1,
            "maxMuscles": 15,
            "joint_mutation_magnitude": 10.0,
            "nn_mutation_magnitude": 0.1,
        }

    @pytest.fixture
    def initial_population(self, default_settings):
        population = []
        for i in range(default_settings["population_size"]):
            creature = create_dummy_creature(num_joints=random.randint(default_settings["minJoints"], default_settings["maxJoints"]))
            creature.fitness = i * 10
            population.append(creature)
        return population

    def test_population_size_constant(self, initial_population, default_settings):
        new_population = evolve_population(initial_population, default_settings)
        assert len(new_population) == default_settings["population_size"]

    def test_fitter_creatures_selected(self, initial_population, default_settings):
        initial_population.sort(key=lambda c: c.fitness, reverse=True)
        fittest_creatures_original_data = [
            (c.get_joint_positions(), c.neural_network.get_weights(), c.neural_network.get_biases()) 
            for c in initial_population[:default_settings["elitism_count"]]
        ]
        new_population = evolve_population(initial_population, default_settings)
        new_population_data = [
            (c.get_joint_positions(), c.neural_network.get_weights(), c.neural_network.get_biases()) 
            for c in new_population
        ]
        for original_data in fittest_creatures_original_data:
            found = False
            for new_data in new_population_data:
                if np.array_equal(original_data[0], new_data[0]) and \
                   all(np.array_equal(w1, w2) for w1, w2 in zip(original_data[1], new_data[1])) and \
                   all(np.array_equal(b1, b2) for b1, b2 in zip(original_data[2], new_data[2])):
                    found = True
                    break
            assert found, "Fittest creature not found in new population (elitism failed)."

    def test_new_creatures_generated_and_valid(self, initial_population, default_settings):
        new_population = evolve_population(initial_population, default_settings)
        num_elites = default_settings["elitism_count"]
        assert len(new_population) > num_elites
        for creature in new_population:
            assert isinstance(creature, Creature)
            assert creature.joints is not None
            assert creature.muscles is not None
            assert creature.neural_network is not None
            assert len(creature.joints) >= default_settings["minJoints"]
            assert len(creature.joints) <= default_settings["maxJoints"]
            assert len(creature.muscles) >= default_settings["minMuscles"]

    def test_nn_weight_mutation_applied(self, initial_population, default_settings):
        test_creature = create_dummy_creature(fixed_seed=42)
        test_creature.fitness = 1000
        settings = default_settings.copy()
        settings["population_size"] = 1
        settings["elitism_count"] = 0
        settings["nnWeightMutationChance"] = 100
        settings["jointPositionMutationChance"] = 0
        settings["addRemoveJointMutationChance"] = 0
        settings["addRemoveMuscleMutationChance"] = 0
        settings["nn_mutation_magnitude"] = 10.0
        initial_pop_for_test = [test_creature]
        original_weights = [w.copy() for w in test_creature.neural_network.get_weights()]
        original_biases = [b.copy() for b in test_creature.neural_network.get_biases()]
        new_population = evolve_population(initial_pop_for_test, settings)
        mutated_creature = new_population[0]
        mutated_weights = mutated_creature.neural_network.get_weights()
        mutated_biases = mutated_creature.neural_network.get_biases()
        weights_mutated = any(not np.array_equal(original_weights[i], mutated_weights[i]) for i in range(len(original_weights)))
        biases_mutated = any(not np.array_equal(original_biases[i], mutated_biases[i]) for i in range(len(original_biases)))
        assert weights_mutated or biases_mutated, "NN weights or biases should have mutated but did not."

    @patch('random.random', return_value=0.01)
    def test_joint_position_mutation_applied(self, mock_random, initial_population, default_settings):
        test_creature = create_dummy_creature(fixed_seed=43, num_joints=default_settings["minJoints"])
        test_creature.fitness = 1000
        settings = default_settings.copy()
        settings["population_size"] = 1
        settings["elitism_count"] = 0
        settings["jointPositionMutationChance"] = 100
        settings["nnWeightMutationChance"] = 0
        settings["addRemoveJointMutationChance"] = 0
        settings["addRemoveMuscleMutationChance"] = 0
        initial_pop_for_test = [test_creature]
        original_positions = [j.position.copy() for j in test_creature.joints]
        new_population = evolve_population(initial_pop_for_test, settings)
        mutated_creature = new_population[0]
        mutated_positions = [j.position for j in mutated_creature.joints]
        positions_changed = False
        for i in range(len(original_positions)):
            if not np.array_equal(original_positions[i], mutated_positions[i]):
                positions_changed = True
                break
        assert positions_changed, "Joint positions should have mutated but did not."

    def test_add_joint_mutation_applied(self, initial_population, default_settings):
        settings = default_settings.copy()
        settings["population_size"] = 1
        settings["elitism_count"] = 0
        settings["addRemoveJointMutationChance"] = 100
        settings["nnWeightMutationChance"] = 0
        settings["jointPositionMutationChance"] = 0
        settings["addRemoveMuscleMutationChance"] = 0
        test_creature = create_dummy_creature(fixed_seed=44, num_joints=settings["minJoints"])
        test_creature.fitness = 1000
        original_joint_count = len(test_creature.joints)
        with patch('random.random', return_value=0.01):
            with patch('random.choice', side_effect=DynamicSideEffect([test_creature, 'add', test_creature.joints[0]] + [0] * 20)):
                new_population = evolve_population([test_creature], settings)
        mutated_creature = new_population[0]
        new_joint_count = len(mutated_creature.joints)
        assert new_joint_count >= original_joint_count, "Joint count should not decrease when starting at minJoints"
        assert new_joint_count <= settings["maxJoints"], "Joint count exceeded maxJoints limit."
        if original_joint_count < settings["maxJoints"]:
            assert new_joint_count > original_joint_count, "A joint should have been added."

    @patch('random.random', return_value=0.01)
    @patch('random.sample', return_value=[0, 1])
    def test_remove_joint_mutation_applied(self, mock_random, initial_population, default_settings):
        settings = default_settings.copy()
        settings["population_size"] = 1
        settings["elitism_count"] = 0
        settings["addRemoveJointMutationChance"] = 100
        settings["nnWeightMutationChance"] = 0
        settings["jointPositionMutationChance"] = 0
        settings["addRemoveMuscleMutationChance"] = 0
        test_creature = create_dummy_creature(fixed_seed=45, num_joints=settings["maxJoints"])
        test_creature.fitness = 1000
        original_joint_count = len(test_creature.joints)
        with patch('random.choice', side_effect=DynamicSideEffect([test_creature, 'remove', 0] + [lambda l: l[0] if l else None] * 20)):
            new_population = evolve_population([test_creature], settings)
        mutated_creature = new_population[0]
        new_joint_count = len(mutated_creature.joints)
        assert new_joint_count <= original_joint_count, "Joint count should not increase when starting at maxJoints"
        assert new_joint_count >= settings["minJoints"], "Joint count went below minJoints limit."
        if original_joint_count > settings["minJoints"]:
            assert new_joint_count < original_joint_count, "A joint should have been removed."

    @patch('random.random', return_value=0.01)
    @patch('random.sample', return_value=[0, 1]) # Mock random.sample for _add_remove_muscle
    def test_add_muscle_mutation_applied(self, mock_random, mock_sample, initial_population, default_settings):
        settings = default_settings.copy()
        settings["population_size"] = 1
        settings["elitism_count"] = 0
        settings["addRemoveMuscleMutationChance"] = 100
        settings["nnWeightMutationChance"] = 0
        settings["jointPositionMutationChance"] = 0
        settings["addRemoveJointMutationChance"] = 0
        test_creature = create_dummy_creature(fixed_seed=46, num_muscles=settings["minMuscles"])
        test_creature.fitness = 1000
        original_muscle_count = len(test_creature.muscles)
        with patch('random.choice', side_effect=DynamicSideEffect([test_creature, 'add'])):
            new_population = evolve_population([test_creature], settings)
        mutated_creature = new_population[0]
        new_muscle_count = len(mutated_creature.muscles)
        assert new_muscle_count >= original_muscle_count, "Muscle count should not decrease when starting at minMuscles"
        assert new_muscle_count <= settings["maxMuscles"], "Muscle count exceeded maxMuscles limit."
        if original_muscle_count < settings["maxMuscles"]:
            assert new_muscle_count > original_muscle_count, "A muscle should have been added."

    @patch('random.random', return_value=0.01)
    def test_remove_muscle_mutation_applied(self, mock_random, initial_population, default_settings):
        settings = default_settings.copy()
        settings["population_size"] = 1
        settings["elitism_count"] = 0
        settings["addRemoveMuscleMutationChance"] = 100
        settings["nnWeightMutationChance"] = 0
        settings["jointPositionMutationChance"] = 0
        settings["addRemoveJointMutationChance"] = 0
        test_creature = create_dummy_creature(fixed_seed=47, num_muscles=settings["maxMuscles"])
        test_creature.fitness = 1000
        original_muscle_count = len(test_creature.muscles)
        with patch('random.choice') as mock_random_choice:
            mock_random_choice.side_effect = DynamicSideEffect([test_creature, 'remove', lambda muscles: muscles[0] if muscles else None])
            new_population = evolve_population([test_creature], settings)
        mutated_creature = new_population[0]
        new_muscle_count = len(mutated_creature.muscles)
        assert new_muscle_count <= original_muscle_count, "Muscle count should not increase when starting at maxMuscles"
        assert new_muscle_count >= settings["minMuscles"], "Muscle count went below minMuscles limit."
        if original_muscle_count > settings["minMuscles"]:
            assert new_muscle_count < original_muscle_count, "A muscle should have been removed."

    @patch('src.evolution.genetic_algorithm._repair_creature_connectivity', return_value=None)
    def test_min_max_joints_respected_during_mutation(self, mock_repair, default_settings):
        settings = default_settings.copy()
        settings["population_size"] = 2
        settings["elitism_count"] = 0
        settings["addRemoveJointMutationChance"] = 100
        settings["nnWeightMutationChance"] = 0
        settings["jointPositionMutationChance"] = 0
        settings["addRemoveMuscleMutationChance"] = 0
        creature_at_min = create_dummy_creature(num_joints=settings["minJoints"], fixed_seed=100)
        creature_at_min.fitness = 100
        creature_at_max = create_dummy_creature(num_joints=settings["maxJoints"], fixed_seed=101)
        creature_at_max.fitness = 100
        population = [creature_at_min, creature_at_max]
        side_effects = [
            creature_at_min, # Parent for child 1
            'add',           # Action for joint mutation for child 1
            creature_at_min.joints[0], # Joint object choice for add (for parent_joint = random.choice(creature.joints))
            creature_at_max, # Parent for child 2
            'remove',        # Action for joint mutation for child 2
            0                # Joint index choice for remove (random.choice(range(len(joints))))
        ] + [create_mock_creature_class()()] * 10 # Fallback for any extra random.choice calls that might expect a Creature
        with patch('random.choice', side_effect=DynamicSideEffect(side_effects)), \
             patch('random.random', side_effect=DynamicSideEffect([0.01] * 8)), \
             patch('random.sample', return_value=[0,1]):
            new_population = evolve_population(population, settings)
            assert len(new_population) == 2
            joint_counts = sorted([len(c.joints) for c in new_population])
            expected_counts = [4, 7]
            assert joint_counts == expected_counts, f"Expected joint counts {expected_counts} but got {joint_counts}"
            for creature in new_population:
                assert settings["minJoints"] <= len(creature.joints) <= settings["maxJoints"]

    def test_empty_initial_population(self, default_settings):
        new_population = evolve_population([], default_settings)
        assert len(new_population) == 0, "Evolving an empty population should result in an empty population."

    def test_invalid_mutation_chance_settings(self, initial_population, default_settings):
        settings_invalid_chance = default_settings.copy()
        settings_invalid_chance["nnWeightMutationChance"] = 150
        try:
            new_population = evolve_population(initial_population, settings_invalid_chance)
            assert len(new_population) == default_settings["population_size"]
        except Exception as e:
            pytest.fail(f"evolve_population crashed with invalid mutation chance: {e}")

    def test_random_seed_for_reproducibility(self, default_settings):
        settings = default_settings.copy()
        settings["population_size"] = 5
        settings["elitism_count"] = 1
        settings["nnWeightMutationChance"] = 100
        settings["jointPositionMutationChance"] = 100
        settings["addRemoveJointMutationChance"] = 100
        settings["addRemoveMuscleMutationChance"] = 100
        random.seed(42)
        np.random.seed(42)
        pop1 = []
        for i in range(settings["population_size"]):
            c = create_dummy_creature(fixed_seed=42+i, num_joints=random.randint(settings["minJoints"], settings["maxJoints"]))
            c.fitness = i * 10
            pop1.append(c)
        evolved_pop1 = evolve_population(pop1, settings)
        random.seed(42)
        np.random.seed(42)
        pop2 = []
        for i in range(settings["population_size"]):
            c = create_dummy_creature(fixed_seed=42+i, num_joints=random.randint(settings["minJoints"], settings["maxJoints"]))
            c.fitness = i * 10
            pop2.append(c)
        evolved_pop2 = evolve_population(pop2, settings)
        assert len(evolved_pop1) == len(evolved_pop2)
        for i in range(len(evolved_pop1)):
            c1 = evolved_pop1[i]
            c2 = evolved_pop2[i]
            assert np.array_equal(c1.get_joint_positions(), c2.get_joint_positions()), f"Joint positions differ at index {i}"
            assert c1.get_muscle_connectivity() == c2.get_muscle_connectivity(), f"Muscle connectivity differs at index {i}"
            weights1 = c1.neural_network.get_weights()
            weights2 = c2.neural_network.get_weights()
            biases1 = c1.neural_network.get_biases()
            biases2 = c2.neural_network.get_biases()
            assert len(weights1) == len(weights2)
            assert all(np.array_equal(w1, w2) for w1, w2 in zip(weights1, weights2)), f"NN weights differ at index {i}"
            assert len(biases1) == len(biases2)
            assert all(np.array_equal(b1, b2) for b1, b2 in zip(biases1, biases2)), f"NN biases differ at index {i}"

    def test_add_muscle_mutation_updates_nn_topology(self):
        # 1. Create a Creature instance with 3 joints and 0 muscles.
        joint1 = Joint(x=0, y=0, mass=1.0)
        joint2 = Joint(x=10, y=0, mass=1.0)
        joint3 = Joint(x=20, y=0, mass=1.0)
        initial_joints = [joint1, joint2, joint3]
        initial_muscles = []

        # Calculate expected initial input size based on 3 joints and 0 muscles
        # (len(joints) * 4 for x,y,vx,vy) + (len(muscles) * 2 for muscle_length, muscle_velocity)
        initial_input_size = (len(initial_joints) * 4) + (len(initial_muscles) * 2) # (3*4) + (0*2) = 12

        # Set output_size to 1 since we expect one muscle after mutation, to avoid issues with 0 output size.
        initial_nn = MockNeuralNetwork(input_size=initial_input_size, output_size=1, hidden_layers=[4])
        creature = Creature(initial_joints, initial_muscles, initial_nn)

        # Verify initial state
        assert creature.neural_network.input_size == initial_input_size

        # Minimal necessary settings for _add_remove_muscle
        settings = {
            "minMuscles": 0, # Allow starting with 0 muscles for this test
            "maxMuscles": 15, # Needs to allow adding
            "minJoints": 3, # Required by _add_remove_muscle for joint selection
            "maxJoints": 8, # Required by _add_remove_muscle for joint selection
        }

        # 2. Ensure random.choice is mocked to return 'add' for the mutation action.
        # 3. Ensure random.sample is mocked to return a valid pair of indices (e.g., [0, 1])
        with patch('random.choice', return_value='add'), \
             patch('random.sample', return_value=[0, 1]):
            # Directly call _add_remove_muscle(creature, settings)
            _add_remove_muscle(creature, settings)

        # 4. Assert that the creature.neural_network.input_size attribute has been updated
        # A new muscle was added, so muscles count becomes 1
        expected_new_input_size = (len(creature.joints) * 4) + (len(creature.muscles) * 2) # (3*4) + (1*2) = 12 + 2 = 14
        assert creature.neural_network.input_size == expected_new_input_size, f"Neural network input_size not updated after adding muscle. Expected {expected_new_input_size}, got {creature.neural_network.input_size}"

    @patch('src.evolution.genetic_algorithm._repair_creature_connectivity', return_value=None)
    def test_single_parent_reproduction_logic(self, mock_repair, default_settings):
        population_size = 10
        elitism_count = 2
        nn_mutation_magnitude = 0.05 # Smaller magnitude for easier approximation checks

        settings = default_settings.copy()
        settings["population_size"] = population_size
        settings["elitism_count"] = elitism_count
        settings["nn_mutation_magnitude"] = nn_mutation_magnitude
        settings["nnWeightMutationChance"] = 100 # Ensure mutation happens for non-elites
        settings["jointPositionMutationChance"] = 0 # Disable other mutations for this test
        settings["addRemoveJointMutationChance"] = 0
        settings["addRemoveMuscleMutationChance"] = 0

        initial_population = []
        # Create 10 creatures with distinct fitness
        for i in range(population_size):
            # Use hidden_layers=[] to test direct input-output layer shaping in MockNeuralNetwork
            creature = create_dummy_creature(num_joints=4, num_muscles=2, hidden_layers=[]) 
            creature.fitness = (population_size - 1 - i) * 10 # Fitness: 90, 80, ..., 0
            initial_population.append(creature)

        # Sort to easily identify top 2
        initial_population.sort(key=lambda c: c.fitness, reverse=True)

        # Manually set identifiable values in NN weights for the top 2 and others
        # Top 1 (fitness 90): value 2.0
        # Top 2 (fitness 80): value 1.0
        # Others (fitness 70, 60, ...): value 0.5
        
        initial_population[0].neural_network.weights[0][0][0] = 2.0 # Fittest
        initial_population[1].neural_network.weights[0][0][0] = 1.0 # Second fittest

        # Set others to 0.5
        for i in range(elitism_count, population_size):
            initial_population[i].neural_network.weights[0][0][0] = 0.5
            
        # Store original elites' full state for exact comparison
        original_elites_data = []
        for i in range(elitism_count):
            c = initial_population[i]
            original_elites_data.append({
                "joints": [j.position.copy() for j in c.joints],
                "muscles": [(m.joint1_idx, m.joint2_idx) for m in c.muscles], # Simplified connectivity check
                "nn_weights": [w.copy() for w in c.neural_network.get_weights()],
                "nn_biases": [b.copy() for b in c.neural_network.get_biases()]
            })

        # Evolve population
        # Mock random.choice for parent selection to ensure only top parents are chosen
        num_offspring = population_size - elitism_count # 8 offspring

        full_side_effects = []
        for i in range(num_offspring):
            full_side_effects.append(initial_population[i % elitism_count]) # Parent selection

        
        with patch('random.choice', side_effect=DynamicSideEffect(full_side_effects)):
            new_population = evolve_population(initial_population, settings)

        # Assert new generation has same population size
        assert len(new_population) == population_size, "New population size mismatch."

        # Assert that the new generation's elites are exact copies of the initial elites


        for i in range(elitism_count):
            original_elite = initial_population[i] # Initial population is already sorted by fitness
            new_elite = new_population[i] # New population is now sorted, so top 'i' should be elites

            # Compare joint positions
            assert all(np.array_equal(oj.position, nj.position) for oj, nj in zip(original_elite.joints, new_elite.joints)), f"Elite {i} joint positions differ."
            # Compare muscle connectivity (simplified)
            original_muscle_conn = [(m.joint1_idx, m.joint2_idx) for m in original_elite.muscles]
            new_muscle_conn = [(m.joint1_idx, m.joint2_idx) for m in new_elite.muscles]
            assert original_muscle_conn == new_muscle_conn, f"Elite {i} muscle connectivity differs."
            # Compare NN weights
            assert all(np.array_equal(ow, nw) for ow, nw in zip(original_elite.neural_network.get_weights(), new_elite.neural_network.get_weights())), f"Elite {i} NN weights differ."
            # Compare NN biases
            assert all(np.array_equal(ob, nb) for ob, nb in zip(original_elite.neural_network.get_biases(), new_elite.neural_network.get_biases())), f"Elite {i} NN biases differ."

        # Crucially, for the non-elite children, assert their neural network's identifiable value
        # (weights[0][0][0]) is approximately equal to *one* of the top two fittest parents' unique values
        # (allowing for mutation magnitude), and *not* a blended value (which would indicate crossover)
        # or a value from the bottom 50% (which indicates genetic material from discarded creatures).

        parent1_val = 2.0
        parent2_val = 1.0
        blended_val = (parent1_val + parent2_val) / 2.0
        other_parent_val = 0.5 # Values from non-elite parents

        # Tolerance for approximation
        tolerance = nn_mutation_magnitude * 2 # Allow for some mutation around the parent value

        # Filter out elites from the new population to check children
        children = new_population[elitism_count:]

        assert len(children) == (population_size - elitism_count), "Incorrect number of children to test."

        for child in children:
            child_val = child.neural_network.weights[0][0][0]

            # Check if it's approximately equal to parent1_val OR parent2_val
            is_from_parent1 = np.isclose(child_val, parent1_val, atol=tolerance)
            is_from_parent2 = np.isclose(child_val, parent2_val, atol=tolerance)
            
            # Check if it's approximately equal to the blended value (expected to fail here)
            is_blended = np.isclose(child_val, blended_val, atol=tolerance)

            # Check if it's approximately equal to the value from other parents (should not be)
            is_from_other = np.isclose(child_val, other_parent_val, atol=tolerance)

            # Assertion for single-parent reproduction: should be from either parent1 or parent2, not blended, not from others.
            # This assertion is designed to FAIL with two-parent crossover.
            assert (is_from_parent1 or is_from_parent2) and not is_blended and not is_from_other, \
                'Child NN weight[0][0][0] ({}) is not from a single top parent. Expected ~{} or ~{}. Is blended? {} (expected False). Is from other? {} (expected False).'.format(
                    child_val, parent1_val, parent2_val, is_blended, is_from_other
                )

    @patch('src.creature.creature.Creature', new_callable=create_mock_creature_class)
    @patch('src.evolution.genetic_algorithm._repair_creature_connectivity', return_value=None)
    def test_single_parent_reproduction_rigorous_id_tracking(self, mock_repair, MockCreatureClass, default_settings):
        MockCreatureClass._next_id = 0 # Ensure ID counter starts clean
        population_size = 10
        elitism_percentage = 0.5 # 50%
        elitism_count = int(population_size * elitism_percentage) # 5

        settings = default_settings.copy()
        settings["population_size"] = population_size
        settings["elitism_count"] = elitism_count
        settings["nnWeightMutationChance"] = 100 # Ensure mutation for non-elites
        settings["jointPositionMutationChance"] = 0 # Disable other mutations
        settings["addRemoveJointMutationChance"] = 0
        settings["addRemoveMuscleMutationChance"] = 0
        settings["nn_mutation_magnitude"] = 0.1 # For distinguishing mutated offspring

        # 1. Create a mock population of 10 creatures with unique IDs and distinct fitness
        initial_population = []
        # Assign fitness in descending order so creature_0 is fittest, creature_9 is least fit
        for i in range(population_size):
            creature_id = f'creature_{i}'
            fitness_score = population_size - 1 - i # 9, 8, ..., 0
            nn = MockNeuralNetwork(1, 1, []) # Minimal NN for mutation tracking
            creature = MockCreatureClass(id=creature_id, fitness=fitness_score, neural_network=nn, num_joints=4, num_muscles=2)
            initial_population.append(creature)

        # Store original creature IDs and their full states for comparison
        original_ids = {c.id for c in initial_population}
        original_creature_states = {c.id: {
            "nn_weights": [w.copy() for w in c.neural_network.get_weights()],
            "nn_biases": [b.copy() for b in c.neural_network.get_biases()]
        } for c in initial_population}

        # Identify top 50% and bottom 50% IDs from original population based on fitness
        sorted_initial_population = sorted(initial_population, key=lambda c: c.fitness, reverse=True)
        original_elite_creatures = sorted_initial_population[:elitism_count]
        original_elite_ids = {c.id for c in original_elite_creatures}

        original_non_elite_creatures = sorted_initial_population[elitism_count:]
        original_non_elite_ids = {c.id for c in original_non_elite_creatures}

        # 2. Call evolve_population
        # Mock random.choice for parent selection.
        # It will pick parents for 5 offspring (10 - 5 elites).
        # Assuming parents are chosen from the top 5 fittest.
        num_offspring = population_size - elitism_count # 5 offspring
        full_random_choice_sequence = []
        for i in range(num_offspring):
            full_random_choice_sequence.append(sorted_initial_population[i % elitism_count]) # Parent selection
        
        with patch('random.choice', side_effect=DynamicSideEffect(full_random_choice_sequence)), \
             patch('random.random', side_effect=DynamicSideEffect([0.01] * 20)):
            new_population = evolve_population(initial_population, settings)

        # 3. Assert new_population size
        assert len(new_population) == population_size, f"New population size mismatch. Expected {population_size}, got {len(new_population)}."

        # Sort new population by fitness to match expected elite order (evolve_population returns sorted list)
        new_population.sort(key=lambda c: c.fitness, reverse=True)
        new_population_ids = {c.id for c in new_population}

        # 5. Assert elite preservation (top 50% are present and are the exact original instances)
        elites_in_new_pop = new_population[:elitism_count]
        elites_in_new_pop_ids = {c.id for c in elites_in_new_pop}

        assert elites_in_new_pop_ids == original_elite_ids, \
            f"Elites in new population ({elites_in_new_pop_ids}) do not match original top 50% ({original_elite_ids})."
        
        # Additionally, verify that these elite creatures are literally the same objects (or their deep copies with same attributes)
        # as the original elites. evolve_population should be copying them directly.
        # Check by comparing their attributes.
        for i in range(elitism_count):
            original_elite = sorted_initial_population[i]
            new_elite = new_population[i]

            assert original_elite.id == new_elite.id, f"Elite at index {i} has different ID. Expected {original_elite.id}, got {new_elite.id}"
            assert original_elite.fitness == new_elite.fitness, f"Elite {original_elite.id} fitness changed."
            # Verify NN equality for elites (no mutation)
            original_elite_weights = original_elite.neural_network.get_weights()
            new_elite_weights = new_elite.neural_network.get_weights()
            assert all(np.array_equal(w1, w2) for w1, w2 in zip(original_elite_weights, new_elite_weights)), \
                f"Elite {original_elite.id} NN weights mutated when it shouldn't have."
            original_elite_biases = original_elite.neural_network.get_biases()
            new_elite_biases = new_elite.neural_network.get_biases()
            assert all(np.array_equal(b1, b2) for b1, b2 in zip(original_elite_biases, new_elite_biases)), \
                f"Elite {original_elite.id} NN biases mutated when it shouldn't have."


        # 6. Assert bottom 50% exclusion
        for bottom_id in original_non_elite_ids:
            assert bottom_id not in new_population_ids, \
                f"Creature with ID {bottom_id} (from bottom 50%) should not be in new population."

        # 7. Verify new, mutated offspring
        # Offspring are the creatures in the new population that are *not* elites
        offspring_in_new_pop = new_population[elitism_count:]
        offspring_ids = {c.id for c in offspring_in_new_pop}

        # Verify exactly 5 new creatures (not in original_ids)
        newly_generated_offspring_ids = offspring_ids.difference(original_ids)
        assert len(newly_generated_offspring_ids) == (population_size - elitism_count), \
            f"Expected {population_size - elitism_count} new offspring, but got {len(newly_generated_offspring_ids)} (IDs: {newly_generated_offspring_ids})."
        
        # Verify offspring are distinct from parents (mutation applied) and have parent_id
        for offspring in offspring_in_new_pop:
            assert offspring.id in newly_generated_offspring_ids, \
                f"Offspring {offspring.id} is not a newly generated ID."
            assert hasattr(offspring, 'parent_id') and offspring.parent_id is not None, \
                f"Offspring {offspring.id} has no parent_id or it is None."
            assert offspring.parent_id in original_ids, \
                f"Offspring {offspring.id} parent_id {offspring.parent_id} not found in original population."

            # Verify mutation by comparing offspring's NN to its parent's original NN
            parent_original_state = original_creature_states[offspring.parent_id]
            offspring_weights = offspring.neural_network.get_weights()
            offspring_biases = offspring.neural_network.get_biases()

            weights_changed = any(not np.array_equal(ow, nw) for ow, nw in zip(parent_original_state["nn_weights"], offspring_weights))
            biases_changed = any(not np.array_equal(ob, nb) for ob, nb in zip(parent_original_state["nn_biases"], offspring_biases))
            
            assert weights_changed or biases_changed, \
                f"Offspring {offspring.id} (parent {offspring.parent_id}) NN weights or biases did not mutate as expected."
