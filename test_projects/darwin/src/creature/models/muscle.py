import numpy as np

class Muscle:
    def __init__(self, joint1_idx: int, joint2_idx: int, initial_length: float, stiffness: float, damping_coefficient: float):
        '''
        Initializes a Muscle object.

        Args:
            joint1_idx (int): Index of the first connected joint.
            joint2_idx (int): Index of the second connected joint.
            initial_length (float): The initial resting length of the muscle.
                                    Must be non-negative.
            stiffness (float): The stiffness of the muscle (spring constant).
                               Must be non-negative.
            damping_coefficient (float): The damping coefficient of the muscle.
                                         Must be non-negative.
        '''
        if not all(isinstance(arg, int) for arg in [joint1_idx, joint2_idx]):
            raise TypeError("joint1_idx and joint2_idx must be integers.")
        if not all(isinstance(arg, (int, float)) for arg in [initial_length, stiffness, damping_coefficient]):
            raise TypeError("initial_length, stiffness, and damping_coefficient must be numbers.")

        if initial_length < 0:
            raise ValueError("Initial length cannot be negative.")
        if stiffness < 0:
            raise ValueError("Stiffness cannot be negative.")
        if damping_coefficient < 0:
            raise ValueError("Damping coefficient cannot be negative.")

        self.joint1_idx = joint1_idx
        self.joint2_idx = joint2_idx
        self.initial_length = initial_length
        self.stiffness = stiffness
        self.damping_coefficient = damping_coefficient
        self.current_resting_length = initial_length # Used for dynamic contraction

    def __repr__(self):
        return f"Muscle(j1_idx={self.joint1_idx}, j2_idx={self.joint2_idx}, init_len={self.initial_length:.2f}, stiff={self.stiffness:.2f}, damp_coeff={self.damping_coefficient:.2f}, curr_rest_len={self.current_resting_length:.2f})"

    def calculate_force(self, joint1_position: np.ndarray, joint2_position: np.ndarray,
                        joint1_velocity: np.ndarray, joint2_velocity: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        '''
        Calculates the force exerted by the muscle on its connected joints.
        The force is calculated based on Hooke\'s Law for spring force and includes damping.

        Args:
            joint1_position (np.ndarray): The 2D position vector of the first connected joint.
            joint2_position (np.ndarray): The 2D position vector of the second connected joint.
            joint1_velocity (np.ndarray): The 2D velocity vector of the first connected joint.
            joint2_velocity (np.ndarray): The 2D velocity vector of the second connected joint.

        Returns:
            tuple: A tuple containing two numpy arrays representing the force
                   to be applied to joint1 and joint2, respectively.
                   force_on_joint1 acts on joint1, force_on_joint2 acts on joint2.
        '''
        # Vector from joint1 to joint2
        vec = joint2_position - joint1_position
        current_length = np.linalg.norm(vec)

        if current_length == 0:
            # If joints are at the exact same position, the length is zero.
            # This prevents division by zero when calculating unit_vec.
            # In this scenario, the spring force is zero (no extension/compression).
            # Damping force would also be zero if relative velocity is zero.
            # If relative velocity is non-zero but current_length is zero,
            # this is an edge case that might indicate an issue in the simulation or
            # extremely high forces. For now, we return zero force to avoid errors.
            return np.array([0.0, 0.0]), np.array([0.0, 0.0])

        unit_vec = vec / current_length # Unit vector pointing from joint1 to joint2

        # Spring force: F_s = -k * (current_length - resting_length) * unit_vec
        # This force acts on joint2. If current_length > resting_length (stretched),
        # (current_length - resting_length) is positive, so force_s is in -unit_vec direction (pulls joint2 towards joint1).
        # If current_length < resting_length (compressed),
        # (current_length - resting_length) is negative, so force_s is in +unit_vec direction (pushes joint2 away from joint1).
        spring_force_magnitude = -self.stiffness * (current_length - self.current_resting_length)
        force_s = spring_force_magnitude * unit_vec

        # Damping force: F_d = -b * v_rel_along_muscle * unit_vec
        # v_rel_along_muscle is the component of relative velocity (joint2 - joint1) along the muscle axis.
        relative_velocity = joint2_velocity - joint1_velocity
        rel_vel_along_muscle = np.dot(relative_velocity, unit_vec)

        # If rel_vel_along_muscle > 0 (joints moving apart), force_d is in -unit_vec direction (resists separation).
        # If rel_vel_along_muscle < 0 (joints moving together), force_d is in +unit_vec direction (resists compression).
        damping_force_magnitude = -self.damping_coefficient * rel_vel_along_muscle
        force_d = damping_force_magnitude * unit_vec

        # Total force on joint2 (from muscle)
        force_on_joint2 = force_s + force_d
        # Force on joint1 is equal and opposite
        force_on_joint1 = -force_on_joint2

        return force_on_joint1, force_on_joint2
