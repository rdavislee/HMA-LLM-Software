import pymunk
import pymunk.autogeometry
import numpy as np
from typing import List, Tuple, Dict

# Assuming these imports are available in the environment
from src.creature.creature import Creature
from src.creature.models.joint import Joint
from src.creature.models.muscle import Muscle
from src.neural_network.network import Network # Not directly used but good to have for context


# Constants for the simulation
# Gravity constant for Y-down coordinate system (positive means downwards).
# Scaled for pixels from Darwin.md's g = 9.81 m/s^2.
GRAVITY_Y = 981.0
# Darwin.md: Simulation timestep: 1/60 second (60 FPS)
TIME_STEP = 1.0 / 60.0
# Darwin.md: Simulation duration: 10 seconds per creature evaluation (600 frames)
SIMULATION_DURATION = 10.0
# Arbitrary radius for Pymunk circle shapes, not specified in docs.
JOINT_RADIUS = 1.0
GROUND_COLLISION_TYPE = 1
JOINT_COLLISION_TYPE = 2
GROUND_CATEGORY = 0b1       # Bit 0
JOINT_CATEGORY = 0b10      # Bit 1 (for creature joints)

def ground_joint_pre_solve(arbiter, space, data):
    """
    Pre-solve collision callback to prevent ground penetration.
    This is called before each collision is resolved.
    """
    # Apply additional collision response for high velocity impacts
    shapes = arbiter.shapes
    if len(shapes) == 2:
        # Find the joint (non-static) body
        joint_body = None
        for shape in shapes:
            if shape.body.body_type != pymunk.Body.STATIC:
                joint_body = shape.body
                break
        
        if joint_body:
            # Only apply damping for extremely high velocities to prevent tunneling
            if joint_body.velocity.y > 1500.0:  # Only for very high downward velocity
                joint_body.velocity = (joint_body.velocity.x * 0.9, joint_body.velocity.y * 0.7)
    
    return True

def ground_joint_post_solve(arbiter, space, data):
    """
    Post-solve collision callback to enforce position constraints.
    This is called after each collision is resolved.
    """
    ground_height = data.get('ground_height', 400.0)
    shapes = arbiter.shapes
    if len(shapes) == 2:
        # Find the joint (non-static) body and shape
        joint_body = None
        joint_shape = None
        for shape in shapes:
            if shape.body.body_type != pymunk.Body.STATIC:
                joint_body = shape.body
                joint_shape = shape
                break
        
        if joint_body and joint_shape:
            # Enforce position constraint if joint has penetrated the ground
            max_allowed_y = ground_height - JOINT_RADIUS
            if joint_body.position.y > max_allowed_y:
                # Force the position to be at the ground surface
                joint_body.position = (joint_body.position.x, max_allowed_y)
                # Reduce downward velocity to prevent bouncing through
                if joint_body.velocity.y > 0:
                    joint_body.velocity = (joint_body.velocity.x, joint_body.velocity.y * 0.3)




def calculate_center_of_mass_x(pymunk_bodies: List[pymunk.Body], creature_joints: List[Joint]) -> float:
    '''
    Calculates the x-coordinate of the center of mass for a creature.
    '''
    total_mass = sum(joint.mass for joint in creature_joints)
    if total_mass == 0:
        # If no joints or all joints have zero mass, CoM is undefined or at origin.
        # For simulation purposes, return 0.0 to avoid division by zero.
        return 0.0

    weighted_x_sum = sum(body.position.x * creature_joints[i].mass for i, body in enumerate(pymunk_bodies))
    return weighted_x_sum / total_mass


def simulate_creature(creature: Creature, settings: Dict) -> Tuple[List[List[float]], float, List[float], List[Tuple[int, int]]]:
    '''
    Simulates a creature's movement using Pymunk and returns playback data and fitness.

    Args:
        creature (Creature): The creature object to simulate.
        settings (Dict): Dictionary containing simulation settings.
                         Expected keys include:
                         - 'groundFriction'
                         - 'springStiffness'
                         - 'minSpringRest' (percentage)
                         - 'maxSpringRest' (percentage)

    Returns:
        Tuple[List[List[float]], float]: A tuple containing:
            - playback_data (List[List[float]]): A list of frames, where each frame
              is a flattened list of joint (x, y) positions: [x0, y0, x1, y1, ...].
            - fitness (float): The creature's fitness, calculated as the change
              in its center of mass x-position from start to end.
    '''

    space = pymunk.Space()
    space.iterations = settings.get('space_iterations', 5000)
    space.gravity = settings.get('gravity', (0, GRAVITY_Y))
    space.damping = settings.get('damping', 0.99)
    space.collision_slop = 0.05  # Reduced for better collision detection at high velocities
    space.bias_coef = 0.7  # Increased for more aggressive collision resolution
    space.sleep_time_threshold = float('inf')
    ground_friction = settings.get('groundFriction', settings.get('ground_friction', 0.5))

    # Add ground plane at y = 0
    # Darwin.md: Ground plane at y = 0 with configurable friction coefficient
    # TRY pymunk.Body(body_type=pymunk.Body.STATIC)
    ground_height_val = settings.get('ground_height', 400.0)
    ground_shape = pymunk.Segment(space.static_body, (-10000, ground_height_val), (10000, ground_height_val), 12) # Ground at the specified height
    ground_shape.friction = ground_friction
    ground_shape.elasticity = 0.0
    ground_shape.collision_type = GROUND_COLLISION_TYPE
    ground_shape.filter = pymunk.ShapeFilter(group=0, categories=GROUND_CATEGORY, mask=JOINT_CATEGORY) # Explicitly set ground group to 0
    space.add(ground_shape)
    # Use on_collision for collision handling as per documentation.md
    space.on_collision(GROUND_COLLISION_TYPE, JOINT_COLLISION_TYPE, 
                      pre_solve=ground_joint_pre_solve, 
                      post_solve=ground_joint_post_solve,
                      data={'ground_height': ground_height_val})




    pymunk_bodies: List[pymunk.Body] = []
    pymunk_shapes: List[pymunk.Shape] = []
    pymunk_springs: List[pymunk.DampedSpring] = []

    # Map creature joints to pymunk bodies and shapes
    for i, joint in enumerate(creature.joints):
        # Use joint.mass from the Creature.Joint object.
        # Ensure mass is positive for Pymunk bodies.
        mass = max(0.1, joint.mass) # Fallback to 1.0 if mass is zero or negative

        # Pymunk moment_for_circle needs a radius.
        inertia = pymunk.moment_for_circle(mass, 0, JOINT_RADIUS, (0,0))
        body = pymunk.Body(mass, inertia)
        body.velocity_limit = 2000.0  # Reduced velocity limit for better collision detection
        ground_height_val = settings.get('ground_height', 400.0)
        # Ensure the joint's initial position doesn't start inside the ground
        adjusted_y = min(joint.y, ground_height_val - JOINT_RADIUS - 1e-4)
        body.position = (joint.x, adjusted_y)
        body.velocity = (joint.vx, joint.vy)

        shape = pymunk.Circle(body, JOINT_RADIUS)
        shape.friction = ground_friction # Apply friction to shapes too
        shape.elasticity = 0.0 # Set elasticity to 0 to prevent bounce/penetration

        body.mass = mass # Re-assign mass after density might have reset it
        body.moment = inertia # Re-assign moment after density might have reset it
        shape.collision_type = JOINT_COLLISION_TYPE # Default density, can be adjusted if needed for visual properties
        shape.filter = pymunk.ShapeFilter(group=id(creature), categories=JOINT_CATEGORY, mask=GROUND_CATEGORY) # Joints in group 1 do not collide with each other

        space.add(body, shape)
        pymunk_bodies.append(body)
        pymunk_shapes.append(shape)

    # Capture the ORIGINAL initial positions of creature joints for playback data
    # This is distinct from the adjusted Pymunk body positions.
    original_initial_positions: List[float] = []
    for joint in creature.joints:
        original_initial_positions.append(joint.x)
        original_initial_positions.append(joint.y)

    # Map creature muscles to pymunk damped springs
    for i, muscle in enumerate(creature.muscles):
        body1 = pymunk_bodies[muscle.joint1_idx]
        body2 = pymunk_bodies[muscle.joint2_idx]

        rest_length = muscle.initial_length
        stiffness = settings.get('springStiffness', 100.0)
        damping = muscle.damping_coefficient

        spring = pymunk.DampedSpring(body1, body2, (0,0), (0,0), rest_length, stiffness, damping)
        space.add(spring)
        pymunk_springs.append(spring)

    # Store initial positions for fitness calculation
    initial_center_of_mass_x = calculate_center_of_mass_x(pymunk_bodies, creature.joints)

    playback_data: List[List[float]] = []
    num_frames = int(settings.get('simulation_duration', SIMULATION_DURATION) / TIME_STEP)

    # Simulation loop
    for frame_idx in range(num_frames):
        # Neural Network Input Collection
        # Based on creature.py's Network instantiation: input_size = len(self.joints) * 4 + len(self.muscles)
        # This implies: (x, y, vx, vy) for each joint, then (current_muscle_length) for each muscle.
        nn_inputs = []
        for body_idx, body in enumerate(pymunk_bodies):
            # Use current Pymunk body's position and velocity
            nn_inputs.append(body.position.x)
            nn_inputs.append(body.position.y)
            nn_inputs.append(body.velocity.x)
            nn_inputs.append(body.velocity.y)
        
        for muscle_idx, muscle_obj in enumerate(creature.muscles):
            # Get current length from the corresponding Pymunk spring
            spring_obj = pymunk_springs[muscle_idx]
            nn_inputs.append(spring_obj.a.position.get_distance(spring_obj.b.position)) # Distance is current length of the spring
            nn_inputs.append(muscle_obj.current_resting_length)

        nn_inputs_array = np.array(nn_inputs, dtype=np.float32)
        # Verify NN input size
        expected_nn_input_len = (len(creature.joints) * 4) + (len(creature.muscles) * 2)
        if creature.neural_network is not None and len(nn_inputs) != creature.neural_network.input_size:
            print(f"WARNING: Neural network input size mismatch! Expected {creature.neural_network.input_size}, but collected {len(nn_inputs)}. Fixing Network's input_size is outside pymunk_engine.py scope.")

        # Neural Network Prediction
        nn_outputs = []
        if creature.neural_network is not None:
            nn_outputs = creature.neural_network.predict(nn_inputs_array)

        # Apply Muscle Control: Update resting lengths of Pymunk springs
        # Darwin.md: Mapped to [min_rest%, max_rest%] of initial muscle length
        min_spring_rest_percent = settings.get('minSpringRest', 50) / 100.0
        max_spring_rest_percent = settings.get('maxSpringRest', 150) / 100.0

        for muscle_idx in range(min(len(creature.muscles), len(nn_outputs))):
            output = nn_outputs[muscle_idx]
            muscle_obj = creature.muscles[muscle_idx]
            spring_obj = pymunk_springs[muscle_idx]

            # Calculate the range for the resting length based on initial_length
            min_resting_length = muscle_obj.initial_length * min_spring_rest_percent
            max_resting_length = muscle_obj.initial_length * max_spring_rest_percent

            # Map the NN output (0-1) to the new resting length
            new_resting_length = min_resting_length + output * (max_resting_length - min_resting_length)
            
            # Ensure new_resting_length is a finite number and within bounds
            if not np.isfinite(new_resting_length):
                # If NN output was NaN/inf, default to initial length
                new_resting_length = muscle_obj.initial_length
            
            # Clamp the new_resting_length to the allowed range
            new_resting_length = max(min_resting_length, min(max_resting_length, new_resting_length))
            
            # Update Pymunk spring's rest_length
            spring_obj.rest_length = new_resting_length
            # Update the creature's muscle object's current_resting_length for next NN input
            # This is crucial because creature.py's NN input calculation uses this.
            muscle_obj.current_resting_length = new_resting_length

        # Step the physics simulation
        space.step(TIME_STEP)

        # Record playback data
        # Format: [x0, y0, x1, y1, ..., xN, yN]
        frame_positions: List[float] = []
        for body in pymunk_bodies:
            frame_positions.append(body.position.x)
            frame_positions.append(body.position.y)
        playback_data.append(frame_positions)

    # Calculate final fitness
    final_center_of_mass_x = calculate_center_of_mass_x(pymunk_bodies, creature.joints)
    fitness = final_center_of_mass_x - initial_center_of_mass_x

    muscle_connectivity = creature.get_muscle_connectivity()

    return playback_data, fitness, original_initial_positions, muscle_connectivity