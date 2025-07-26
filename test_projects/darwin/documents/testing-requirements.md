# Testing Requirements

This document outlines the comprehensive testing strategy for the Evolution Simulator backend. All tests must pass for the project to be considered complete.

## 1. Unit Tests

These tests focus on isolating individual components and verifying their correctness in a controlled environment.

- **Physics Engine:**
  - `test_spring_force_calculation`: Verify that the force exerted by a muscle (spring) is correctly calculated based on its current length, resting length, and stiffness.
  - `test_ground_collision_response`: Ensure that when a joint's y-position is less than or equal to 0, a correct normal force is applied to prevent penetration.
  - `test_ground_friction`: Verify that a friction force opposing horizontal movement is correctly applied when a joint is in contact with the ground.
  - `test_physics_integration_step`: Check that a single step of the physics integrator (e.g., Verlet) correctly updates a joint's position and velocity based on applied forces.

- **Neural Network:**
  - `test_forward_pass`: With a known set of weights and inputs, verify that the neural network produces the expected output.
  - `test_activation_functions`: Test `tanh` and `sigmoid` activation functions with known inputs.

- **Genetic Algorithm:**
  - `test_weight_mutation`: Verify that the NN weight mutation applies a small random change to a weight when triggered.
  - `test_position_mutation`: Ensure joint position mutation correctly offsets a joint's coordinates.
  - `test_add_joint_mutation`: Check that a new joint is added correctly, respecting the `max_joints` constraint and maintaining graph connectivity.
  - `test_remove_joint_mutation`: Verify that a joint is removed, connected muscles are handled, and the `min_joints` constraint is respected.
  - `test_add_muscle_mutation`: Ensure a new muscle is added between two previously unconnected joints.
  - `test_remove_muscle_mutation`: Verify a muscle is correctly removed, ensuring the creature remains a single connected graph.

- **Creature & Fitness:**
  - `test_fitness_calculation`: For a creature with a known, pre-calculated trajectory, verify that the fitness function returns the correct value (change in center of mass X).
  - `test_center_of_mass_calculation`: Ensure the center of mass is calculated correctly based on joint positions and weights.

## 2. Integration Tests

These tests verify the interaction between different modules and the overall system behavior.

- **Simulation Integrity & Determinism:**
  - `test_deterministic_simulation`: A full simulation run with a fixed random seed must produce the exact same final population, fitness scores, and playback data every time it is run.

- **Physics & World Rules:**
  - `test_no_ground_penetration`: Throughout an entire simulation, no joint's y-coordinate should ever be less than 0.
  - `test_energy_conservation`: For a creature simulated in a world with no friction or external forces (e.g., in mid-air), the total energy of the system should remain constant or decrease slightly due to damping, but never increase.

- **Evolutionary & Population Rules:**
  - `test_evolutionary_progress`: While not a strict guarantee, the best fitness of generation `N+1` should generally be greater than or equal to the best fitness of generation `N`. This test can run for a few generations and assert a non-decreasing trend.
  - `test_population_size_consistency`: After the selection and reproduction phase of each generation, the population size must be exactly 100.
  - `test_creature_topology_constraints`: After any mutation, the number of joints per creature must always be within the `minJoints` and `maxJoints` settings.
  - `test_creature_graph_connectivity`: After any mutation (especially removing joints or muscles), verify that the creature's muscle-joint graph remains a single connected component.

- **API Contract Adherence:**
  - `test_api_run_endpoint`: Send a valid request to `POST /api/evolution/run` and verify the response format matches the specification (e.g., `{"runId": "..."}`).
  - `test_api_results_endpoint`: After a simulation, call `GET /api/evolution/results/{runId}` and validate the entire response schema, including the types and structure of `playbackData`, `fitnessScores`, `initialPositions`, and `muscleConnectivity`.
  - `test_api_results_sorting`: Verify that the top-level arrays in the results response are all sorted in parallel based on `fitnessScores` in descending order.

## 3. Performance Tests

These tests ensure the system meets performance and resource usage requirements.

- **Simulation Speed:**
  - `test_full_run_timing`: A full simulation run (e.g., 10 generations, 100 creatures, 10-second simulation each) should complete within a reasonable time benchmark (e.g., under 60 seconds).
- **Memory Usage:**
  - `test_memory_stability`: Monitor memory usage across multiple generations to ensure it does not grow unboundedly. It should remain relatively stable after the first few generations.
