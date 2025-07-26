import random
import copy
import numpy as np
from typing import List, Dict, Any, Tuple

from src.creature.creature import Creature
from src.creature.models.joint import Joint
from src.creature.models.muscle import Muscle
from src.neural_network.network import Network

def evolve_population(population: List[Creature], settings: Dict[str, Any]) -> List[Creature]:
    '''
    Evolves the population of creatures through selection, reproduction, and mutation.

    Args:
        population (List[Creature]): A list of Creature objects, each expected to have a 'fitness' attribute.
        settings (Dict[str, Any]): A dictionary containing simulation settings, including
                                   mutation chances and creature constraints.

    Returns:
        List[Creature]: The new generation of creatures.
    '''
    # 1. Selection
    # Sort population by fitness in descending order. This is crucial for selecting the fittest
    # individuals for elitism and as parents for the next generation.
    # Assumes Creature objects in the list have a 'fitness' attribute added dynamically by the simulation/test.
    population.sort(key=lambda x: x.fitness, reverse=True)



    num_elites = settings['elitism_count']
    # Ensure num_elites is at least 0 and not more than population size
    num_elites = max(0, min(num_elites, len(population)))
    
    elites = population[:num_elites]

    # 3. For the remaining slots in the new population, select parents from the 'elite' group.
    # If no elites are available (e.g., due to small population size or elitism settings),
    # fall back to selecting from the entire current population to ensure reproduction can occur.
    parent_pool = elites if elites else population

    new_population: List[Creature] = []
    new_population.extend(elites) # Add elites to the new population

    # 2. Reproduction and Mutation
    # Fill the rest of the population until it reaches the original size
    target_population_size = len(population)
    while len(new_population) < target_population_size:
        # Select one parent randomly from the parent pool.
        parent = random.choice(parent_pool)

        # Create a child creature by cloning the selected parent.
        child_creature = parent.clone()

        # Apply mutations to the child
        _apply_mutations(child_creature, settings)

        # Ensure creature constraints (min/max joints) and connectivity are met
        _enforce_creature_constraints(child_creature, settings)

        # Synchronize neural network input topology with creature structure
        expected_input_size = (len(child_creature.joints) * 4) + \
                              (len(child_creature.muscles) * 2)
        if child_creature.neural_network and \
           child_creature.neural_network.input_size != expected_input_size:
            child_creature.neural_network.update_input_topology(expected_input_size)

        # Synchronize neural network output topology with creature structure (muscles)
        expected_output_size = len(child_creature.muscles)
        if child_creature.neural_network and \
           child_creature.neural_network.output_size != expected_output_size:
            child_creature.neural_network.update_output_topology(expected_output_size)

        new_population.append(child_creature)

    # In case of minor discrepancies due to rounding or elite handling, trim or fill to original size
    if len(new_population) > target_population_size:
        new_population = new_population[:target_population_size]


    return new_population

def _apply_mutations(creature: Creature, settings: Dict[str, Any]):
    '''Applies various mutations to the creature based on settings.'''
    # Cap mutation chances at 100% to handle potentially invalid input settings gracefully
    nn_weight_mut_chance = min(100, settings.get("nnWeightMutationChance", 0))
    joint_pos_mut_chance = min(100, settings.get("jointPositionMutationChance", 0))
    add_remove_joint_mut_chance = min(100, settings.get("addRemoveJointMutationChance", 0))
    add_remove_muscle_mut_chance = min(100, settings.get("addRemoveMuscleMutationChance", 0))

    # 1. Neural Network Weight Mutation
    if creature.neural_network and random.random() * 100 < nn_weight_mut_chance:
        _mutate_nn_weights(creature.neural_network, settings)

    # 2. Joint Position Mutation
    if random.random() * 100 < joint_pos_mut_chance:
        _mutate_joint_positions(creature.joints, settings)

    # 3. Add/Remove Joint Mutation
    if random.random() * 100 < add_remove_joint_mut_chance:
        _add_remove_joint(creature, settings)

    # 4. Add/Remove Muscle Mutation
    if random.random() * 100 < add_remove_muscle_mut_chance:
        _add_remove_muscle(creature, settings)

def _mutate_nn_weights(neural_network, settings: Dict[str, Any]):
    '''
    Mutates the weights of the neural network.
    This function is a placeholder. It assumes the neural_network object
    will have a `mutate` method or expose its weights for direct manipulation.
    The actual implementation depends on the `Neural Network Module` (Phase 2).
    '''
    if neural_network: # Check if neural_network object exists
        mutation_magnitude = settings.get("nn_mutation_magnitude", 0.01) # Default to 0.01 if not in settings

        # Mutate weights
        for i in range(len(neural_network.weights)):
            # Add random noise scaled by mutation_magnitude
            neural_network.weights[i] += np.random.randn(*neural_network.weights[i].shape) * mutation_magnitude
        
        # Mutate biases
        for i in range(len(neural_network.biases)):
            # Add random noise scaled by mutation_magnitude
            neural_network.biases[i] += np.random.randn(*neural_network.biases[i].shape) * mutation_magnitude

def _mutate_joint_positions(joints: List[Joint], settings: Dict[str, Any]):
    '''Mutates the positions of existing joints with small random displacements.'''
    mutation_strength = settings.get("jointPositionMutationStrength", 5.0) # Default strength if not in settings
    for joint in joints:
        if not joint.fixed: # Do not mutate fixed joints
            joint.x += random.uniform(-mutation_strength, mutation_strength)
            joint.y += random.uniform(-mutation_strength, mutation_strength)
            joint.y = max(0.0, joint.y) # Ensure joint does not go below ground

def _add_remove_joint(creature: Creature, settings: Dict[str, Any]):
    '''Adds or removes a joint, and adjusts muscles accordingly.'''
    min_joints = settings.get("minJoints", 3)
    max_joints = settings.get("maxJoints", 8)
    current_num_joints = len(creature.joints)

    action = random.choice(["add", "remove"])

    if action == "add" and current_num_joints < max_joints:
        # Add a new joint
        if creature.joints:
            # Position new joint near a random existing joint
            parent_joint = random.choice(creature.joints)
            new_x = parent_joint.x + random.uniform(-20, 20)
            new_y = parent_joint.y + random.uniform(-20, 20)
            new_y = max(0.0, new_y) # Ensure above ground
        else: # Should only happen if starting with 0 joints, which initial population should prevent
            new_x = random.uniform(0, 100)
            new_y = random.uniform(0, 100)

        new_joint = Joint(x=new_x, y=new_y, mass=settings.get("jointWeight", 1.0))
        creature.joints.append(new_joint)
        new_joint_idx = len(creature.joints) - 1

        # Connect the new joint to an existing joint with a new muscle
        if current_num_joints > 0:
            existing_joint_idx = random.randrange(current_num_joints)
            # Avoid duplicate muscles
            if not any((m.joint1_idx == existing_joint_idx and m.joint2_idx == new_joint_idx) or \
                       (m.joint1_idx == new_joint_idx and m.joint2_idx == existing_joint_idx) \
                       for m in creature.muscles):
                
                initial_length = random.uniform(settings.get("minInitialSpringLength", 30),
                                                settings.get("maxInitialSpringLength", 70))
                muscle_strength = settings.get("springStiffness", 100)
                target_length = random.uniform(settings.get("minSpringRest", 50),
                                               settings.get("maxSpringRest", 150))

                new_muscle = Muscle(existing_joint_idx, new_joint_idx, initial_length, muscle_strength, target_length)
                creature.muscles.append(new_muscle)
        
        # Update neural network input topology after adding joint/muscle
        new_input_size = (len(creature.joints) * 4) + (len(creature.muscles) * 2)
        if creature.neural_network:
            creature.neural_network.update_input_topology(new_input_size)
    elif action == "remove" and current_num_joints > min_joints:
        # Remove an existing joint, excluding fixed joints
        removable_joints_indices = [i for i, j in enumerate(creature.joints) if not j.fixed]
        if not removable_joints_indices:
            return # No non-fixed joints to remove

        joint_to_remove_idx = random.choice(removable_joints_indices)

        # Remove all muscles connected to the joint being removed
        creature.muscles = [m for m in creature.muscles if m.joint1_idx != joint_to_remove_idx and m.joint2_idx != joint_to_remove_idx]

        # Remove the joint itself
        del creature.joints[joint_to_remove_idx]

        # Update muscle indices to reflect the removal (indices shift down)
        for muscle in creature.muscles:
            if muscle.joint1_idx > joint_to_remove_idx:
                muscle.joint1_idx -= 1
            if muscle.joint2_idx > joint_to_remove_idx:
                muscle.joint2_idx -= 1
        
        # Update neural network input topology after removing joint/muscle
        new_input_size = (len(creature.joints) * 4) + (len(creature.muscles) * 2)
        if creature.neural_network:
            creature.neural_network.update_input_topology(new_input_size)

def _add_remove_muscle(creature: Creature, settings: Dict[str, Any]):
    '''Adds or removes a muscle between joints.'''
    action = random.choice(["add", "remove"])
    num_joints = len(creature.joints)

    if num_joints < 2: # Cannot add or remove muscles if less than 2 joints
        return

    if action == "add":
        attempts = 0
        max_attempts = 10 # Limit attempts to find a valid pair
        while attempts < max_attempts:
            j1_idx, j2_idx = random.sample(range(num_joints), 2) # Pick two distinct joints
            
            # Check if muscle already exists
            if not any((m.joint1_idx == j1_idx and m.joint2_idx == j2_idx) or \
                       (m.joint1_idx == j2_idx and m.joint2_idx == j1_idx) \
                       for m in creature.muscles):
                
                initial_length = random.uniform(settings.get("minInitialSpringLength", 30),
                                                settings.get("maxInitialSpringLength", 70))
                muscle_strength = settings.get("springStiffness", 100)
                target_length = random.uniform(settings.get("minSpringRest", 50),
                                               settings.get("maxSpringRest", 150))

                new_muscle = Muscle(j1_idx, j2_idx, initial_length, muscle_strength, target_length)
                creature.muscles.append(new_muscle)
                new_input_size = (len(creature.joints) * 4) + (len(creature.muscles) * 2)
                if creature.neural_network:
                    creature.neural_network.update_input_topology(new_input_size)
                break # Successfully added muscle
            attempts += 1

    elif action == "remove" and len(creature.muscles) > 0:
        # Remove a random muscle
        muscle_to_remove = random.choice(creature.muscles)
        creature.muscles.remove(muscle_to_remove)
        new_input_size = (len(creature.joints) * 4) + (len(creature.muscles) * 2)
        if creature.neural_network:
            creature.neural_network.update_input_topology(new_input_size)

def _enforce_creature_constraints(creature: Creature, settings: Dict[str, Any]):
    '''
    Ensures the creature adheres to min/max joint constraints and maintains connectivity.
    This function acts as a post-mutation repair mechanism.
    '''
    min_joints = settings.get("minJoints", 3)
    max_joints = settings.get("maxJoints", 8)

    # If too many joints, remove randomly until within limits
    while len(creature.joints) > max_joints:
        removable_joints_indices = [i for i, j in enumerate(creature.joints) if not j.fixed]
        if not removable_joints_indices:
            break # No non-fixed joints to remove
        joint_to_remove_idx = random.choice(removable_joints_indices)
        
        creature.muscles = [m for m in creature.muscles if m.joint1_idx != joint_to_remove_idx and m.joint2_idx != joint_to_remove_idx]
        del creature.joints[joint_to_remove_idx]

        for muscle in creature.muscles:
            if muscle.joint1_idx > joint_to_remove_idx:
                muscle.joint1_idx -= 1
            if muscle.joint2_idx > joint_to_remove_idx:
                muscle.joint2_idx -= 1
        
        # Update neural network input topology after removing joint/muscle
        new_input_size = (len(creature.joints) * 4) + (len(creature.muscles) * 2)
        if creature.neural_network:
            creature.neural_network.update_input_topology(new_input_size)

    # If too few joints, add until within limits
    while len(creature.joints) < min_joints:
        current_num_joints = len(creature.joints)
        if not creature.joints: # If creature is completely empty, create a first joint
            new_x = random.uniform(0, 100)
            new_y = random.uniform(0, 100)
            new_joint = Joint(x=new_x, y=new_y, mass=settings.get("jointWeight", 1.0))
            creature.joints.append(new_joint)
            # No muscle added yet for the very first joint
        else:
            # Replicate the "add" logic from _add_remove_joint directly here
            parent_joint = random.choice(creature.joints)
            new_x = parent_joint.x + random.uniform(-20, 20)
            new_y = parent_joint.y + random.uniform(-20, 20)
            new_y = max(0.0, new_y) # Ensure above ground

            new_joint = Joint(x=new_x, y=new_y, mass=settings.get("jointWeight", 1.0))
            creature.joints.append(new_joint)
            new_joint_idx = len(creature.joints) - 1

            # Connect the new joint to an existing joint with a new muscle
            if current_num_joints > 0:
                existing_joint_idx = random.randrange(current_num_joints)
                # Avoid duplicate muscles
                if not any((m.joint1_idx == existing_joint_idx and m.joint2_idx == new_joint_idx) or \
                           (m.joint1_idx == new_joint_idx and m.joint2_idx == existing_joint_idx) \
                           for m in creature.muscles):
                    
                    initial_length = random.uniform(settings.get("minInitialSpringLength", 30),
                                                    settings.get("maxInitialSpringLength", 70))
                    muscle_strength = settings.get("springStiffness", 100)
                    target_length = random.uniform(settings.get("minSpringRest", 50),
                                                   settings.get("maxSpringRest", 150))

                    new_muscle = Muscle(existing_joint_idx, new_joint_idx, initial_length, muscle_strength, target_length)
                    creature.muscles.append(new_muscle)
            
        # Update neural network input topology after adding joint/muscle
        new_input_size = (len(creature.joints) * 4) + (len(creature.muscles) * 2)
        if creature.neural_network:
            creature.neural_network.update_input_topology(new_input_size)

    # Ensure creature remains a single connected graph after all modifications
    _repair_creature_connectivity(creature, settings)


def _is_creature_connected(creature: Creature) -> bool:
    '''Checks if the creature\'s joints form a single connected graph using BFS.'''
    num_joints = len(creature.joints)
    if num_joints == 0:
        return True # An empty creature is vacuously connected
    if num_joints > 1 and not creature.muscles:
        return False # Multiple joints with no muscles means disconnected

    # Build adjacency list from muscles
    adj = {i: [] for i in range(num_joints)}
    for muscle in creature.muscles:
        adj[muscle.joint1_idx].append(muscle.joint2_idx)
        adj[muscle.joint2_idx].append(muscle.joint1_idx)

    # Perform BFS starting from the first joint
    visited = [False] * num_joints
    queue = [0]
    visited[0] = True
    count = 1

    head = 0
    while head < len(queue):
        u = queue[head]
        head += 1
        for v in adj[u]:
            if not visited[v]:
                visited[v] = True
                queue.append(v)
                count += 1
    
    return count == num_joints

def _repair_creature_connectivity(creature: Creature, settings: Dict[str, Any]):
    '''Attempts to repair a disconnected creature by adding muscles between components.'''
    if _is_creature_connected(creature):
        return

    num_joints = len(creature.joints)
    if num_joints < 2:
        return # Cannot connect if less than 2 joints

    # Find all disconnected components
    adj = {i: [] for i in range(num_joints)}
    for muscle in creature.muscles:
        adj[muscle.joint1_idx].append(muscle.joint2_idx)
        adj[muscle.joint2_idx].append(muscle.joint1_idx)

    visited = [False] * num_joints
    components = []

    for i in range(num_joints):
        if not visited[i]:
            current_component = []
            queue = [i]
            visited[i] = True
            head = 0
            while head < len(queue):
                u = queue[head]
                head += 1
                current_component.append(u)
                for v in adj[u]:
                    if not visited[v]:
                        visited[v] = True
                        queue.append(v)
            components.append(current_component)

    # Connect components if there's more than one
    if len(components) > 1:
        # Connect each component to the next one in the list
        for i in range(len(components) - 1):
            comp1_nodes = components[i]
            comp2_nodes = components[i+1]

            # Pick a random joint from each component to create a new muscle between
            j1_idx = random.choice(comp1_nodes)
            j2_idx = random.choice(comp2_nodes)

            # Only add if a muscle doesn't already exist between these two joints
            if not any((m.joint1_idx == j1_idx and m.joint2_idx == j2_idx) or \
                       (m.joint1_idx == j2_idx and m.joint2_idx == j1_idx) \
                       for m in creature.muscles):

                initial_length = random.uniform(settings.get("minInitialSpringLength", 30),
                                                settings.get("maxInitialSpringLength", 70))
                muscle_strength = settings.get("springStiffness", 100)
                target_length = random.uniform(settings.get("minSpringRest", 50),
                                               settings.get("maxSpringRest", 150))

                new_muscle = Muscle(j1_idx, j2_idx, initial_length, muscle_strength, target_length)
                creature.muscles.append(new_muscle)
                # Update neural network input topology after adding muscle
                new_input_size = (len(creature.joints) * 4) + (len(creature.muscles) * 2)
                if creature.neural_network:
                    creature.neural_network.update_input_topology(new_input_size)
                # After adding a muscle, re-check connectivity. If it's fully connected, we can stop.
                if _is_creature_connected(creature):
                    break
