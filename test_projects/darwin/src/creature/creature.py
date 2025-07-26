from typing import List, Tuple, Optional
from src.creature.models.joint import Joint
from src.creature.models.muscle import Muscle
from src.neural_network.network import Network

_DEFAULT_NETWORK = object()
class Creature:
    '''
    Represents a creature composed of joints (masses) and muscles (springs),
    controlled by a neural network.
    '''
    def __init__(self, joints: List[Joint], muscles: List[Muscle], neural_network: Optional[Network] = _DEFAULT_NETWORK):
        '''
        Initializes a Creature instance.

        Args:
            joints (List[Joint]): A list of Joint objects defining the creature's nodes.
            muscles (List[Muscle]): A list of Muscle objects defining the connections
                                    and spring properties between joints.
            neural_network: The neural network controlling the creature's muscles.
                            Expected to be an instance of NeuralNetwork once implemented.
                            Use _DEFAULT_NETWORK to signal default initialization.
        '''
        for i, joint in enumerate(joints):
            if not isinstance(joint, Joint):
                raise TypeError(f"All items in 'joints' must be instances of Joint, but item at index {i} is {type(joint).__name__}.")
        self.joints: List[Joint] = joints
        if not self.joints:
            raise ValueError("Creature must have at least one joint.")

        for i, muscle in enumerate(muscles):
            if not isinstance(muscle, Muscle):
                raise TypeError(f"All items in 'muscles' must be instances of Muscle, but item at index {i} is {type(muscle).__name__}.")
        self.muscles: List[Muscle] = muscles
        
        if neural_network is _DEFAULT_NETWORK:
            if self.muscles:
                input_size = (len(self.joints) * 4) + (len(self.muscles) * 2)
                output_size = len(self.muscles)
                hidden_layer_sizes = [len(self.muscles) * 2]
                self.neural_network = Network(input_size=input_size, output_size=output_size, hidden_layer_sizes=hidden_layer_sizes)
            else:
                self.neural_network = None
        elif neural_network is None:
            self.neural_network = None
        else:
            self.neural_network = neural_network

    def get_joint_positions(self) -> List[float]:
        '''
        Returns a flattened list of all joint (x, y) positions.
        Format: [x0, y0, x1, y1, ..., xN, yN]
        This format is required for 'playbackData' in the API response.
        '''
        positions = []
        for joint in self.joints:
            positions.append(joint.x)
            positions.append(joint.y)
        return positions

    def get_muscle_connectivity(self) -> List[List[int]]:
        '''
        Returns a list of tuples representing muscle connectivity.
        Each tuple contains the indices of the two joints connected by a muscle.
        Format: [(joint1_idx_0, joint2_idx_0), ..., (joint1_idx_M, joint2_idx_M)]
        This format is required for 'muscleConnectivity' in the API response.
        '''
        connectivity = []
        for muscle in self.muscles:
            connectivity.append([muscle.joint1_idx, muscle.joint2_idx])
        return connectivity

    def get_initial_joint_positions(self) -> List[float]:
        '''
        Returns a flattened list of the creature's initial joint (x, y) positions.
        This method assumes that the 'initial' state is captured at the point
        this creature object is first created or reset.
        In a full simulation, this might be a stored property rather than dynamically
        derived, depending on the simulation's state management.
        '''
        # For the purpose of this class definition, we'll assume the initial
        # positions are the current positions when this method is called.
        # A more robust system might store initial_x, initial_y on the Joint object
        # or as a separate property of the Creature.
        return self.get_joint_positions()

    def clone(self) -> 'Creature':
        '''
        Creates a completely independent deep copy of the creature.
        All joints, muscles, and the neural network (if present) are new instances.
        '''
        cloned_joints = []
        for joint in self.joints:
            # Deep copy all relevant attributes for Joint
            cloned_joints.append(Joint(x=joint.x, y=joint.y, mass=joint.mass,
                                       vx=joint.vx, vy=joint.vy,
                                       ax=joint.ax, ay=joint.ay,
                                       fixed=joint.fixed))

        cloned_muscles = []
        for muscle in self.muscles:
            # Create a new Muscle instance with its initial properties
            new_muscle = Muscle(
                joint1_idx=muscle.joint1_idx,
                joint2_idx=muscle.joint2_idx,
                initial_length=muscle.initial_length,
                stiffness=muscle.stiffness,
                damping_coefficient=muscle.damping_coefficient
            )
            # Crucially, deep copy the current_resting_length as it can change during simulation
            new_muscle.current_resting_length = muscle.current_resting_length
            cloned_muscles.append(new_muscle)

        cloned_neural_network = None
        if self.neural_network is not None:
            # Call the neural network's own clone method for deep copy
            cloned_neural_network = self.neural_network.clone()

        return Creature(joints=cloned_joints, muscles=cloned_muscles, neural_network=cloned_neural_network)
