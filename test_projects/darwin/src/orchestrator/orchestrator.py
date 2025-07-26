import uuid
import random
import numpy as np
from typing import List

from src.creature.creature import Creature
from src.creature.models.joint import Joint
from src.creature.models.muscle import Muscle
from src.physics.pymunk_engine import simulate_creature
from src.neural_network.network import Network
from src.evolution.genetic_algorithm import evolve_population

def run_simulation(settings: dict, generations: int) -> dict:
    '''
    Manages the overall simulation loop for creature evolution.

    Args:
        settings (dict): Dictionary containing simulation settings.
        generations (int): Number of generations to simulate.

    Returns:
        dict: A dictionary containing playbackData, fitnessScores, initialPositions, muscleConnectivity
              for the best creature of the final generation, formatted for the API.
    '''
    if not isinstance(generations, int) or generations <= 0:
        raise ValueError("Generations must be a positive integer")
    population_size = 100 # As per documentation, population size is constant at 100

    current_population = []
    # 1. Initialize a population of creatures
    for _ in range(population_size):
        num_joints = random.randint(settings["minJoints"], settings["maxJoints"])
        
        # Ensure at least 2 joints for a functional creature with muscles
        if num_joints < 2:
            num_joints = 2

        # Joints: (x, y) positions. Start them slightly above ground.
        initial_joint_positions_np = np.random.uniform(low=[0, 50], high=[100, 200], size=(num_joints, 2))

        joints_list: List[Joint] = []
        for j_id, pos in enumerate(initial_joint_positions_np):
            joints_list.append(Joint(x=pos[0], y=pos[1], mass=settings["jointWeight"]))

        # Muscles: connections between joints. Ensure connectivity.
        muscles_data_raw = [] # Temporarily store raw connections to build Muscle objects later
        # Create a minimum spanning tree-like structure to ensure connectivity
        if num_joints > 1:
            connected_nodes = {0}
            remaining_nodes = set(range(1, num_joints))
            
            while remaining_nodes:
                u = random.choice(list(connected_nodes))
                v = random.choice(list(remaining_nodes))
                muscles_data_raw.append([u, v])
                connected_nodes.add(v)
                remaining_nodes.remove(v)
            
            num_possible_muscles = num_joints * (num_joints - 1) // 2
            num_to_add = random.randint(0, min(num_joints * 2, num_possible_muscles - len(muscles_data_raw)))
            
            for _ in range(num_to_add):
                j1, j2 = random.sample(range(num_joints), 2)
                if j1 != j2 and ([j1, j2] not in muscles_data_raw and [j2, j1] not in muscles_data_raw):
                    muscles_data_raw.append([j1, j2])

        muscles_list: List[Muscle] = []
        for m_id, (j1_idx, j2_idx) in enumerate(muscles_data_raw):
            initial_length = random.uniform(settings["minInitialSpringLength"], settings["maxInitialSpringLength"])
            
            # Calculate target_length based on initial_length and settings
            min_rest_ratio = settings.get("minSpringRest", 50) / 100.0
            max_rest_ratio = settings.get("maxSpringRest", 150) / 100.0
            target_length = initial_length * random.uniform(min_rest_ratio, max_rest_ratio)
            
            muscles_list.append(Muscle(
                joint1_idx=j1_idx,
                joint2_idx=j2_idx,
                initial_length=initial_length,
                stiffness=settings["springStiffness"],
                damping_coefficient=0.5
            ))

        # Neural Network: Determine input/output sizes based on the generated creature's topology
        # Inputs: Joint positions (2*num_joints), Joint velocities (2*num_joints), Muscle lengths (num_muscles)
        # Outputs: Muscle target lengths (num_muscles)
        nn_input_size = (len(joints_list) * 4) + (len(muscles_list) * 2)
        nn_output_size = len(muscles_list)
        
        # Handle case where a creature might have 0 muscles
        if nn_output_size == 0:
            if num_joints >= 2: # If we have joints, but no muscles, add one for functionality
                # This should ideally not happen with the MST logic, but as a safeguard
                j1_idx, j2_idx = 0, 1
                joint1_pos = np.array(joints_list[j1_idx].position)
                joint2_pos = np.array(joints_list[j2_idx].position)
                initial_length = random.uniform(settings["minInitialSpringLength"], settings["maxInitialSpringLength"])
                min_rest_ratio = settings.get("minSpringRest", 50) / 100.0
                max_rest_ratio = settings.get("maxSpringRest", 150) / 100.0
                target_length = initial_length * random.uniform(min_rest_ratio, max_rest_ratio)
                
                muscles_list.append(Muscle(
                    joint1_idx=j1_idx,
                    joint2_idx=j2_idx,
                    initial_length=initial_length,
                    stiffness=settings["springStiffness"],
                    damping_coefficient=0.5
                ))
                nn_output_size = 1
                nn_input_size = (len(joints_list) * 4) + (len(muscles_list) * 2)

        neural_network = Network(input_size=nn_input_size, output_size=nn_output_size, hidden_layer_sizes=[nn_output_size * 2])
        
        creature = Creature(
            joints=joints_list,
            muscles=muscles_list,
            neural_network=neural_network
        )
        current_population.append(creature)

 # Instantiate PhysicsEngine with settings

    # Variables to store the final generation's data for all creatures
    final_playback_data: List[List[List[float]]] = []
    final_fitness_scores: List[float] = []
    final_initial_positions: List[List[float]] = []
    final_muscle_connectivity: List[List[List[int]]] = []

    if settings.get('orchestratorTestMode') is True:
        settings['simulation_duration'] = 0.1
        print("Orchestrator: 'orchestratorTestMode' is True. Setting simulation_duration to 0.1 for testing.")

    for gen in range(generations):
        print(f"--- Generation {gen + 1}/{generations} ---")
        generation_results = [] # List of (creature, playback_data, initial_positions, muscle_connectivity)
        
        for i, creature in enumerate(current_population):
            expected_input_size = (len(creature.joints) * 4) + (len(creature.muscles) * 2)
            if creature.neural_network is not None and creature.neural_network.input_size != expected_input_size:
                creature.neural_network.update_input_topology(expected_input_size)
            # 3. Use PhysicsEngine.simulate_creature
            # simulate_creature returns (playback_data, final_center_of_mass_x, initial_joint_positions, muscle_connectivity)
            playback_data_single, final_com_x, initial_pos_single, muscle_conn_single = \
                simulate_creature(creature, settings)
            
            # 4. Assign fitness to creature and store in generation_results
            creature.fitness = final_com_x
            generation_results.append((creature, playback_data_single, initial_pos_single, muscle_conn_single))
        
        # Sort creatures by fitness (descending)
        generation_results.sort(key=lambda x: x[0].fitness, reverse=True)
        
        # If this is the final generation, collect data for all creatures
        if gen == generations - 1:
            for creature_res, pb_data, init_pos, muscle_conn in generation_results:
                final_playback_data.append(pb_data)
                final_fitness_scores.append(creature_res.fitness)
                final_initial_positions.append(init_pos)
                final_muscle_connectivity.append(muscle_conn)
            
        # 5. Evolve population for the next generation
        # evolve_population expects population and fitnesses.
        # Pass (creature, fitness) pairs to genetic_algorithm.evolve_population
        creatures_with_fitness = [(res[0], res[0].fitness) for res in generation_results] # (creature, fitness)
        if gen < generations - 1:
            current_population = evolve_population([res[0] for res in generation_results], settings)

    # 6. Return results in the format expected by the API
    return {
        "playbackData": final_playback_data,
        "fitnessScores": final_fitness_scores,
        "initialPositions": final_initial_positions,
        "muscleConnectivity": final_muscle_connectivity
    }