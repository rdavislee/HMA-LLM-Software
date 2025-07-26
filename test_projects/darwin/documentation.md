# Project: Evolution Simulator

## Product Vision
To create a backend for a 2D physics-based evolution simulator. Creatures, composed of joints (masses) and muscles (springs) controlled by a neural network, will evolve over generations to improve their locomotion. The backend will run the simulation and provide results to an existing frontend for visualization.

## Architecture Overview
The system will be a monolithic Python backend service with a REST API. It will be composed of several core modules that work together to run the evolutionary simulation.

- **API Layer (FastAPI):** Exposes endpoints for the frontend to start simulations and retrieve results.
- **Simulation Orchestrator:** Manages the overall process, including generation loops, population management, and calling other modules.
- **Genetic Algorithm Module:** Handles selection, mutation, and reproduction of creatures.
- **Physics Engine Module (Pymunk):** Simulates the 2D world using the Pymunk physics library, which is a wrapper for Chipmunk2D. This provides robust and efficient physics calculations.
- **Neural Network Module:** Evaluates the neural network for each creature to determine muscle actions at each step of the physics simulation.
- **Creature Module:** Defines the data structures for creatures, including their physical topology (joints and muscles) and their neural network "brain".

## Modules

### 1. API Layer
- **Purpose**: To handle HTTP requests from the frontend.
- **Key Interfaces**:
    - `POST /api/evolution/run`: Starts a new simulation run.
    - `GET /api/evolution/results/{runId}`: Retrieves the full playback data for a completed run.
- **Dependencies**: Simulation Orchestrator

### 2. Simulation Orchestrator
- **Purpose**: To manage the main simulation loop.
- **Key Interfaces**: `run_simulation(settings, generations)`
- **Dependencies**: Genetic Algorithm, Physics Engine, Creature Module

### 3. Genetic Algorithm Module
- **Purpose**: To evolve the population of creatures.
- **Key Interfaces**: `evolve_population(population, settings)`
- **Core Logic**: The evolution process must follow a single-parent model. A new creature (child) is a direct, mutated copy of a single selected parent. The previous two-parent crossover logic is incorrect and must be removed.
- **Dependencies**: Creature Module

### 4. Physics Engine Module
- **Purpose**: To simulate one creature's movement for a set duration using the Pymunk library.
- **Key Interfaces**: `simulate_creature(creature, settings)`
- **Dependencies**: Neural Network Module, Pymunk
- **NOTE ON COLLISION HANDLING (FINAL CLARIFICATION)**: There has been significant confusion regarding Pymunk's collision handling. To be perfectly clear: the function `add_collision_handler` **DOES NOT EXIST** in the version of Pymunk being used and must not be called. The correct way to handle collisions is by defining a function and assigning it to the `space.on_collision` property. This function will be called by Pymunk when collisions occur. All collision logic must be implemented using this `space.on_collision` pattern.

### 5. Neural Network Module
- **Purpose**: To compute muscle outputs from sensor inputs.
- **Key Interfaces**: `predict(nn, inputs)`
- **Dependencies**: None

### 6. Creature Module
- **Purpose**: To define the data structures for creatures.
- **Key Interfaces**: `Creature` class/dataclass
- **Dependencies**: None

## API Specification (Source of Truth: Frontend Code)

### POST /api/evolution/run
- **Description**: Kicks off a new evolution simulation.
- **Request Body**: A JSON object with `settings` and `generations` keys. The `settings` object must contain the following camelCase keys:
  ```json
  {
    "settings": {
      "minSpringRest": 50,
      "maxSpringRest": 150,
      "minInitialSpringLength": 30,
      "maxInitialSpringLength": 70,
      "groundFriction": 0.5,
      "jointWeight": 1.0,
      "minJoints": 3,
      "maxJoints": 8,
      "springStiffness": 100,
      "nnWeightMutationChance": 10,
      "jointPositionMutationChance": 5,
      "addRemoveJointMutationChance": 2,
      "addRemoveMuscleMutationChance": 5
    },
    "generations": 10
  }
  ```
- **Response Body**:
  ```json
  {
    "runId": "a-unique-identifier"
  }
  ```

### GET /api/evolution/results/{runId}
- **Description**: Fetches the results for visualization after a run is complete.
- **Response Body**: A JSON object with four keys. All top-level arrays must be sorted in parallel based on `fitnessScores` (descending).
  ```json
  {
    "playbackData": [ /* [creature][frame][flat_joint_positions as x1,y1,x2,y2,...] */ ],
    "fitnessScores": [ /* [fitness_scores] */ ],
    "initialPositions": [ /* [creature][flat_initial_joint_positions as x1,y1,x2,y2,...] */ ],
    "muscleConnectivity": [ /* [creature][muscle][joint1_idx, joint2_idx] */ ]
  }
  ```

## Testing Strategy

### Unit Tests
- **Pymunk Wrapper**: Test the functions that translate our creature models (Joints, Muscles) into Pymunk bodies, shapes, and constraints.
- **Neural Network**: Test the forward pass calculation with known weights and inputs.
- **Genetic Algorithm**: Test each mutation operation individually (weight, position, add/remove joint, add/remove muscle). **The single-parent reproduction logic must also be tested.**
- **Fitness**: Test the fitness calculation for a creature with a known trajectory.
- **Creature Status**: Creatures must be tested to always be fully connected using a BFS.

### Integration Tests
- **Physics & World Rules (New Pymunk-based tests):**
  - `test_gravity_effect`: Verify that a creature created in the air falls downwards over time by checking its center of mass y-coordinate across several frames.
  - `test_no_ground_penetration_on_multiple_runs`: Run 5 separate, deterministic simulations with different seeds. In each simulation, verify that no joint's y-coordinate ever exceeds the ground height (400). This is to catch intermittent physics glitches where joints might temporarily fall through the floor before being corrected.
  - `test_ground_contact`: For a standard creature, at least one of its joints must make contact with the ground (y <= 400) at some point during the simulation.
  - `test_no_joint_to_joint_collision`: A new test to verify that joints can pass through each other freely under gravity.
- **Simulation Integrity & Determinism**:
  - `test_deterministic_simulation`: A full simulation run with a fixed random seed must produce the exact same final population, fitness scores, and playback data every time it is run.
- **Evolutionary & Population Rules**:
  - `test_evolutionary_progress`: The best fitness of generation `N+1` should generally be greater than or equal to the best fitness of generation `N`.
  - `test_population_size_consistency`: After selection and reproduction, the population size must be exactly 100.
  - `test_creature_topology_constraints`: After any mutation, the number of joints per creature must be within the `minJoints` and `maxJoints` settings.
  - `test_creature_graph_connectivity`: After any mutation, the creature's muscle-joint graph must remain a single connected component. This is critical. **Playback data must also be checked to ensure no disconnected joints are present.**
- **API Contract Adherence**:
  - `test_api_run_endpoint`: Verify the `POST /api/evolution/run` endpoint.
  - `test_api_results_endpoint`: Verify the `GET /api/evolution/results/{runId}` endpoint.
  - `test_api_results_sorting`: Verify the results are sorted correctly.

## Development Plan
1.  **Phase 1**: Implement core data structures and the Physics Engine. (Complete)
2.  **Phase 2**: Implement the Neural Network module. (Complete)
3.  **Phase 3**: Implement the Genetic Algorithm. (Complete)
4.  **Phase 4**: Implement the Simulation Orchestrator and API Layer. (Complete)
5.  **Phase 5**: Backend/Frontend Integration. (Complete)
6.  **Phase 6**: Physics Engine Rework and Debugging. (Complete)
7.  **Phase 7**: Final Debugging and Refinement. (Complete)
8.  **Phase 8**: Targeted Human-in-the-Loop Debugging. (Complete)
9.  **Phase 9**: Single-Parent Refactor. (Complete)
10. **Phase 10**: Concurrent Bug Fixing
    - **Objective**: Concurrently resolve two outstanding issues: a physics engine bug causing ground penetration and failing tests in the genetic algorithm module.
    - **Physics Task**: The `test_ground_penetration_with_high_velocity` test in `src/physics/pymunk_engine_test.py` is failing because it uses an insufficient number of physics solver iterations (`space.iterations = 200`). This does not reflect the main simulation's configuration (`5000`). The fix is to update the test to use a higher, more realistic number of iterations (e.g., `5000`) to ensure the test passes and accurately validates the engine's behavior under high velocity.
    - **Genetic Algorithm Task**: The `test_single_parent_reproduction_rigorous_id_tracking` test in `src/evolution/genetic_algorithm_test.py` is failing due to a typo in an assertion's f-string. The variable `top_50_percent_original_ids` needs to be corrected to `original_elite_ids`. This is a minor fix within the test file itself.

## Environment Guide
- **Language**: Python 3.9+
- **Web Framework**: FastAPI
- **Testing Framework**: Pytest
- **Build**: N/A (interpreted language)
- **Test**: `python -m pytest -v`
- **Run**: `python -m uvicorn src.main:app --reload`
- **Key Libraries**:
    - `fastapi`: For the web server API.
    - `uvicorn`: ASGI server for FastAPI.
    - `pytest`: For running the test suite.
    - `numpy`: For numerical calculations.
    - `pymunk`: For 2D physics simulation.
