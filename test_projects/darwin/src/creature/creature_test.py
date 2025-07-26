import pytest
from src.creature.models.joint import Joint
from src.creature.models.muscle import Muscle
from src.creature.creature import Creature
from src.neural_network.network import Network
import numpy as np

# Test Partitions for Joint, Muscle, and Creature Classes

## Joint Class Test Partitions:
# - Initialization:
#     - Valid coordinates (positive, negative, zero).
#     - Valid mass (positive, zero).
#     - Default values for velocity, acceleration, and fixed.
# - Attribute Access:
#     - `x`, `y` coordinates.
#     - `vx`, `vy` velocities.
#     - `ax`, `ay` accelerations.
#     - `mass`.
#     - `fixed`.
# - Methods:
#     - No specific methods defined in `joint.py` based on memory, so focus on properties.

class TestJoint:
    # Covers Initialization and Attribute Access for valid coordinates and mass
    def test_joint_initialization_and_attributes(self):
        joint = Joint(x=1.0, y=2.0, mass=0.5)
        assert joint.x == 1.0
        assert joint.y == 2.0
        assert joint.mass == 0.5
        assert joint.vx == 0.0
        assert joint.vy == 0.0
        assert joint.ax == 0.0
        assert joint.ay == 0.0
        assert joint.fixed == False

    # Covers Initialization with zero coordinates and mass
    def test_joint_initialization_zero_values(self):
        joint = Joint(x=0.0, y=0.0, mass=0.0)
        assert joint.x == 0.0
        assert joint.y == 0.0
        assert joint.mass == 0.0
        assert joint.vx == 0.0
        assert joint.vy == 0.0
        assert joint.ax == 0.0
        assert joint.ay == 0.0
        assert joint.fixed == False

    # Covers Initialization with negative coordinates
    def test_joint_initialization_negative_coordinates(self):
        joint = Joint(x=-1.0, y=-2.0, mass=1.0)
        assert joint.x == -1.0
        assert joint.y == -2.0
        assert joint.mass == 1.0

    # Covers Initialization with custom velocity, acceleration, and fixed
    def test_joint_initialization_custom_defaults(self):
        joint = Joint(x=1.0, y=1.0, mass=1.0, vx=0.1, vy=0.2, ax=0.3, ay=0.4, fixed=True)
        assert joint.vx == 0.1
        assert joint.vy == 0.2
        assert joint.ax == 0.3
        assert joint.ay == 0.4
        assert joint.fixed == True

    # Covers Attribute Access for setting values
    def test_joint_attribute_setting(self):
        joint = Joint(x=0.0, y=0.0, mass=1.0)
        joint.x = 5.0
        joint.y = 6.0
        joint.vx = 0.5
        joint.vy = 0.6
        joint.ax = 0.7
        joint.ay = 0.8
        joint.mass = 2.0
        joint.fixed = True

        assert joint.x == 5.0
        assert joint.y == 6.0
        assert joint.vx == 0.5
        assert joint.vy == 0.6
        assert joint.ax == 0.7
        assert joint.ay == 0.8
        assert joint.mass == 2.0
        assert joint.fixed == True

    # Covers Initialization with invalid mass (negative)
    def test_joint_initialization_invalid_mass(self):
        with pytest.raises(ValueError, match="Mass cannot be negative."):
            Joint(x=1.0, y=2.0, mass=-0.1)

## Muscle Class Test Partitions:
# - Initialization:
#     - Valid `joint1`, `joint2` (indices).
#     - Valid `initial_length` (positive, zero).
#     - Valid `stiffness` (positive, zero).
#     - Valid `damping_coefficient` (positive, zero).
# - Attribute Access:
#     - `joint1_idx`, `joint2_idx`.
#     - `initial_length`.
#     - `stiffness`.
#     - `current_resting_length`.
# - Methods:
#     - No specific methods defined in `muscle.py` based on memory, so focus on properties.

class TestMuscle:
    # Covers Initialization and Attribute Access for valid parameters
    def test_muscle_initialization_and_attributes(self):
        muscle = Muscle(joint1_idx=0, joint2_idx=1, initial_length=10.0, stiffness=1.0, damping_coefficient=0.1)
        assert muscle.joint1_idx == 0
        assert muscle.joint2_idx == 1
        assert muscle.initial_length == 10.0
        assert muscle.stiffness == 1.0
        assert muscle.damping_coefficient == 0.1
        assert muscle.current_resting_length == 10.0 # initial_length is set as current_resting_length in constructor

    # Covers Initialization with different damping_coefficient
    def test_muscle_initialization_different_damping_coefficient(self):
        muscle = Muscle(joint1_idx=0, joint2_idx=1, initial_length=10.0, stiffness=1.0, damping_coefficient=0.5)
        assert muscle.damping_coefficient == 0.5

    # Covers Initialization with zero initial_length and stiffness
    def test_muscle_initialization_zero_values(self):
        muscle = Muscle(joint1_idx=0, joint2_idx=1, initial_length=0.0, stiffness=0.0, damping_coefficient=0.0)
        assert muscle.initial_length == 0.0
        assert muscle.stiffness == 0.0
        assert muscle.damping_coefficient == 0.0
        assert muscle.current_resting_length == 0.0

    # Covers Attribute Access for setting values
    def test_muscle_attribute_setting(self):
        muscle = Muscle(joint1_idx=0, joint2_idx=1, initial_length=10.0, stiffness=1.0, damping_coefficient=0.1)
        muscle.joint1_idx = 2
        muscle.joint2_idx = 3
        muscle.initial_length = 12.0 # This changes initial_length, but current_resting_length remains same until updated by other means
        muscle.stiffness = 1.5
        muscle.damping_coefficient = 0.8
        muscle.current_resting_length = 8.0 # This can be set directly for testing purposes

        assert muscle.joint1_idx == 2
        assert muscle.joint2_idx == 3
        assert muscle.initial_length == 12.0
        assert muscle.stiffness == 1.5
        assert muscle.damping_coefficient == 0.8
        assert muscle.current_resting_length == 8.0

    # Covers Initialization with invalid initial_length (negative)
    def test_muscle_initialization_invalid_initial_length(self):
        with pytest.raises(ValueError, match="Initial length cannot be negative."):
            Muscle(joint1_idx=0, joint2_idx=1, initial_length=-1.0, stiffness=1.0, damping_coefficient=0.1)

    # Covers Initialization with invalid stiffness (negative)
    def test_muscle_initialization_invalid_stiffness(self):
        with pytest.raises(ValueError, match="Stiffness cannot be negative."):
            Muscle(joint1_idx=0, joint2_idx=1, initial_length=10.0, stiffness=-1.0, damping_coefficient=0.1)

    # Covers Initialization with invalid damping_coefficient (negative)
    def test_muscle_initialization_invalid_damping_coefficient(self):
        with pytest.raises(ValueError, match="Damping coefficient cannot be negative."):
            Muscle(joint1_idx=0, joint2_idx=1, initial_length=10.0, stiffness=1.0, damping_coefficient=-1.0)

## Creature Class Test Partitions:
# - Initialization:
#     - Valid `joints` (list of Joint objects).
#     - Valid `muscles` (list of Muscle objects).
#     - Empty `joints` and `muscles` lists.
# - Attribute Access:
#     - `joints`.
#     - `muscles`.
# - Methods:
#     - `clone()`: Deep copy verification (primitive attributes, object instances, neural network independence).

## Creature.clone() Test Partitions:
# - Basic Cloning:
#     - Creature with no neural network.
#     - Creature with a neural network.
# - Deep Copy Verification - Object Identity:
#     - Verify the cloned creature, its joints, muscles, and neural network (if present) are new instances.
#     - Verify neural network's internal weights and biases are new arrays.
# - Deep Copy Verification - Attribute Independence:
#     - Modify attributes of original joints/muscles/NN and ensure clone is unaffected.
#     - Modify attributes of cloned joints/muscles/NN and ensure original is unaffected.

class TestCreature:
    # Covers Initialization and Attribute Access for valid lists of joints and muscles
    def test_creature_initialization_and_attributes(self):
        joint1 = Joint(x=0.0, y=0.0, mass=1.0)
        joint2 = Joint(x=1.0, y=0.0, mass=1.0)
        muscle1 = Muscle(joint1_idx=0, joint2_idx=1, initial_length=1.0, stiffness=1.0, damping_coefficient=0.1)

        joints = [joint1, joint2]
        muscles = [muscle1]

        creature = Creature(joints=joints, muscles=muscles)
        assert creature.joints == joints
        assert creature.muscles == muscles
        assert len(creature.joints) == 2
        assert len(creature.muscles) == 1

    # Covers Initialization with empty lists
    def test_creature_initialization_empty_lists(self):
        with pytest.raises(ValueError, match="Creature must have at least one joint."):
            Creature(joints=[], muscles=[])

    # Covers Initialization with only joints
    def test_creature_initialization_only_joints(self):
        joint1 = Joint(x=0.0, y=0.0, mass=1.0)
        joints = [joint1]
        creature = Creature(joints=joints, muscles=[])
        assert creature.neural_network is None

    # Covers Initialization with only muscles (though less practical, tests constructor)
    def test_creature_initialization_only_muscles(self):
        muscle1 = Muscle(joint1_idx=0, joint2_idx=1, initial_length=1.0, stiffness=1.0, damping_coefficient=0.1)
        muscles = [muscle1]
        with pytest.raises(ValueError, match="Creature must have at least one joint."):
            Creature(joints=[], muscles=muscles)

    # Covers Attribute Access for setting values (though usually passed in constructor)
    def test_creature_attribute_setting(self):
        # Create valid initial components
        initial_joint1 = Joint(x=0.0, y=0.0, mass=1.0)
        initial_joint2 = Joint(x=1.0, y=0.0, mass=1.0)
        initial_muscle1 = Muscle(joint1_idx=0, joint2_idx=1, initial_length=1.0, stiffness=1.0, damping_coefficient=0.1)
        
        # Create new components to set attributes to
        new_joint1 = Joint(x=2.0, y=2.0, mass=2.0)
        new_joint2 = Joint(x=3.0, y=3.0, mass=2.0)
        new_muscle1 = Muscle(joint1_idx=0, joint2_idx=1, initial_length=2.0, stiffness=2.0, damping_coefficient=0.2)

        creature = Creature(joints=[initial_joint1, initial_joint2], muscles=[initial_muscle1])
        
        creature.joints = [new_joint1, new_joint2]
        creature.muscles = [new_muscle1]

        assert creature.joints == [new_joint1, new_joint2]
        assert creature.muscles == [new_muscle1]

    # Covers Initialization with non-Joint object in joints list
    def test_creature_initialization_invalid_joint_type(self):
        with pytest.raises(TypeError, match="All items in 'joints' must be instances of Joint"):
            Creature(joints=["not a joint"], muscles=[])

    # Covers Initialization with non-Muscle object in muscles list
    def test_creature_initialization_invalid_muscle_type(self):
        joint1 = Joint(x=0.0, y=0.0, mass=1.0)
        with pytest.raises(TypeError, match="All items in 'muscles' must be instances of Muscle"):
            Creature(joints=[joint1], muscles=["not a muscle"])


class TestCreatureClone:
    def setup_creature_with_nn(self):
        joint1 = Joint(x=0.0, y=0.0, mass=1.0)
        joint2 = Joint(x=1.0, y=0.0, mass=1.0)
        joint3 = Joint(x=0.0, y=1.0, mass=1.0)
        muscle1 = Muscle(joint1_idx=0, joint2_idx=1, initial_length=1.0, stiffness=1.0, damping_coefficient=0.1)
        muscle2 = Muscle(joint1_idx=1, joint2_idx=2, initial_length=1.0, stiffness=1.0, damping_coefficient=0.1)
        
        joints = [joint1, joint2, joint3]
        muscles = [muscle1, muscle2]

        input_size = (len(joints) * 4) + (len(muscles) * 2)
        output_size = len(muscles)
        hidden_layer_sizes = [4]
        nn = Network(input_size=input_size, output_size=output_size, hidden_layer_sizes=hidden_layer_sizes)
        
        if len(nn.weights) > 0 and nn.weights[0].size > 0:
            nn.weights[0].flat[0] = 0.123
        if len(nn.biases) > 0 and nn.biases[0].size > 0:
            nn.biases[0].flat[0] = 0.456
        
        creature = Creature(joints=joints, muscles=muscles, neural_network=nn)
        return creature

    # Covers Basic Cloning - No NN & Object Identity & Attribute Independence (Primitives)
    def test_clone_no_neural_network_deep_copy(self):
        joint1 = Joint(x=0.0, y=0.0, mass=1.0, vx=0.1, vy=0.2, ax=0.3, ay=0.4, fixed=False)
        joint2 = Joint(x=1.0, y=0.0, mass=2.0, vx=0.5, vy=0.6, ax=0.7, ay=0.8, fixed=True)
        muscle1 = Muscle(joint1_idx=0, joint2_idx=1, initial_length=1.0, stiffness=1.0, damping_coefficient=0.1)
        muscle1.current_resting_length = 0.8 # Modify a mutable attribute

        original_creature = Creature(joints=[joint1, joint2], muscles=[muscle1], neural_network=None)
        cloned_creature = original_creature.clone()

        # 1. Verify creature instance identity
        assert cloned_creature is not original_creature
        assert cloned_creature.neural_network is None
        assert original_creature.neural_network is None

        # 2. Verify joint deep copy
        assert len(cloned_creature.joints) == len(original_creature.joints)
        for i in range(len(original_creature.joints)):
            orig_j = original_creature.joints[i]
            cloned_j = cloned_creature.joints[i]
            assert cloned_j is not orig_j # Must be new instance

            # Primitive attributes copied by value
            assert cloned_j.x == orig_j.x
            assert cloned_j.y == orig_j.y
            assert cloned_j.mass == orig_j.mass
            assert cloned_j.vx == orig_j.vx
            assert cloned_j.vy == orig_j.vy
            assert cloned_j.ax == orig_j.ax
            assert cloned_j.ay == orig_j.ay
            assert cloned_j.fixed == orig_j.fixed
            # Verify numpy arrays are also deep copied
            assert cloned_j.position is not orig_j.position
            assert np.array_equal(cloned_j.position, orig_j.position)
            assert cloned_j.velocity is not orig_j.velocity
            assert np.array_equal(cloned_j.velocity, orig_j.velocity)
            assert cloned_j.acceleration is not orig_j.acceleration
            assert np.array_equal(cloned_j.acceleration, orig_j.acceleration)

            # Modify original and check clone (independence)
            orig_j.x = 99.0 + i
            orig_j.mass = 99.0 + i
            orig_j.fixed = not orig_j.fixed
            orig_j.position[0] = 100.0 + i # Modifying underlying numpy array

            assert cloned_j.x != orig_j.x
            assert cloned_j.mass != orig_j.mass
            assert cloned_j.fixed != orig_j.fixed
            assert cloned_j.position[0] != orig_j.position[0]
            assert cloned_j.x != 100.0 + i # Should still be original x value

            # Modify clone and check original (independence)
            cloned_j.y = 88.0 + i
            cloned_j.vy = 88.0 + i
            cloned_j.position[1] = 200.0 + i # Modifying underlying numpy array

            assert orig_j.y != cloned_j.y
            assert orig_j.vy != cloned_j.vy
            assert orig_j.position[1] != cloned_j.position[1]
            assert orig_j.y != 200.0 + i # Should still be original y value (before original_j.y was changed, if it was)

        # 3. Verify muscle deep copy
        assert len(cloned_creature.muscles) == len(original_creature.muscles)
        for i in range(len(original_creature.muscles)):
            orig_m = original_creature.muscles[i]
            cloned_m = cloned_creature.muscles[i]
            assert cloned_m is not orig_m # Must be new instance

            # Primitive attributes copied by value
            assert cloned_m.joint1_idx == orig_m.joint1_idx
            assert cloned_m.joint2_idx == orig_m.joint2_idx
            assert cloned_m.initial_length == orig_m.initial_length
            assert cloned_m.stiffness == orig_m.stiffness
            assert cloned_m.damping_coefficient == orig_m.damping_coefficient
            assert cloned_m.current_resting_length == orig_m.current_resting_length

            # Modify original and check clone (independence)
            orig_m.initial_length = 99.0 + i
            orig_m.current_resting_length = 88.0 + i

            assert cloned_m.initial_length != orig_m.initial_length
            assert cloned_m.current_resting_length != orig_m.current_resting_length

            # Modify clone and check original (independence)
            cloned_m.stiffness = 77.0 + i
            cloned_m.damping_coefficient = 66.0 + i

            assert orig_m.stiffness != cloned_m.stiffness
            assert orig_m.damping_coefficient != cloned_m.damping_coefficient

    # Covers Basic Cloning - With NN & Object Identity & Attribute Independence (NN)
    def test_clone_with_neural_network_deep_copy(self):
        original_creature = self.setup_creature_with_nn()
        cloned_creature = original_creature.clone()

        # 1. Verify creature instance identity
        assert cloned_creature is not original_creature
        assert cloned_creature.neural_network is not None
        assert original_creature.neural_network is not None

        # 2. Verify neural network deep copy
        orig_nn = original_creature.neural_network
        cloned_nn = cloned_creature.neural_network

        assert cloned_nn is not orig_nn # NN object itself must be a new instance

        # Verify weights and biases are deep copied (new arrays, same values)
        assert len(cloned_nn.weights) == len(orig_nn.weights)
        assert len(cloned_nn.biases) == len(orig_nn.biases)

        for i in range(len(orig_nn.weights)):
            assert cloned_nn.weights[i] is not orig_nn.weights[i] # Each weight matrix must be a new array
            assert np.array_equal(cloned_nn.weights[i], orig_nn.weights[i]) # Values must be the same

            assert cloned_nn.biases[i] is not orig_nn.biases[i] # Each bias vector must be a new array
            assert np.array_equal(cloned_nn.biases[i], orig_nn.biases[i]) # Values must be the same

            # Modify original NN weights/biases and check clone (independence)
            original_weight_val_before_mod = orig_nn.weights[i].flat[0]
            original_bias_val_before_mod = orig_nn.biases[i].flat[0]

            orig_nn.weights[i].flat[0] = 999.999 + i # Modify a value
            orig_nn.biases[i].flat[0] = 888.888 + i # Modify a value

            assert cloned_nn.weights[i].flat[0] == pytest.approx(original_weight_val_before_mod)
            assert cloned_nn.biases[i].flat[0] == pytest.approx(original_bias_val_before_mod)

            # Modify cloned NN weights/biases and check original (independence)
            if cloned_nn.weights[i].size > 1: # Ensure there's another element to modify
                cloned_nn.weights[i].flat[1] = 111.111 + i
            if cloned_nn.biases[i].size > 1:
                cloned_nn.biases[i].flat[1] = 222.222 + i

            # Verify original values are unchanged
            if orig_nn.weights[i].size > 1:
                assert orig_nn.weights[i].flat[1] != pytest.approx(111.111 + i)
            if orig_nn.biases[i].size > 1:
                assert orig_nn.biases[i].flat[1] != pytest.approx(222.222 + i)

    # Covers Basic Cloning - Creature with only joints (no muscles, no NN)
    def test_clone_creature_with_only_joints(self):
        joint1 = Joint(x=0.0, y=0.0, mass=1.0)
        joint2 = Joint(x=1.0, y=0.0, mass=1.0)
        
        original_creature = Creature(joints=[joint1, joint2], muscles=[], neural_network=None)
        cloned_creature = original_creature.clone()

        # Verify creature instance identity
        assert cloned_creature is not original_creature
        assert cloned_creature.neural_network is None
        assert original_creature.neural_network is None
        assert len(cloned_creature.muscles) == 0
        assert len(original_creature.muscles) == 0

        # Verify joint deep copy
        assert len(cloned_creature.joints) == len(original_creature.joints)
        for i in range(len(original_creature.joints)):
            orig_j = original_creature.joints[i]
            cloned_j = cloned_creature.joints[i]
            assert cloned_j is not orig_j # Must be new instance

            # Primitive attributes copied by value
            assert cloned_j.x == orig_j.x
            assert cloned_j.y == orig_j.y
            assert cloned_j.mass == orig_j.mass
            assert cloned_j.fixed == orig_j.fixed
            # Verify numpy arrays are also deep copied
            assert cloned_j.position is not orig_j.position
            assert np.array_equal(cloned_j.position, orig_j.position)

            # Modify original and check clone (independence)
            orig_j.x = 99.0 + i
            orig_j.mass = 99.0 + i
            orig_j.fixed = not orig_j.fixed
            orig_j.position[0] = 100.0 + i # Modifying underlying numpy array

            assert cloned_j.x != orig_j.x
            assert cloned_j.mass != orig_j.mass
            assert cloned_j.fixed != orig_j.fixed
            assert cloned_j.position[0] != orig_j.position[0]

            # Modify clone and check original (independence)
            cloned_j.y = 88.0 + i
            cloned_j.position[1] = 200.0 + i # Modifying underlying numpy array

            assert orig_j.y != cloned_j.y
            assert orig_j.position[1] != cloned_j.position[1]
