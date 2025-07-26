# Evolution Simulator Backend Requirements

## Overview
Build a 2D physics-based evolution simulator where creatures composed of neural networks and spring-mass systems evolve locomotion through natural selection. The system must handle complete physics simulation, neural network evaluation, genetic algorithms, and API endpoints for the frontend.

## Core Components

### 1. Physics Engine

#### World Properties
- 2D world with gravity (g = -9.81 m/s²)
- Ground plane at y = 0 with configurable friction coefficient
- Simulation timestep: 1/60 second (60 FPS)
- Simulation duration: 10 seconds per creature evaluation (600 frames)

#### Creature Physics
- **Joints (Nodes)**:
  - Point masses with configurable weight
  - Position (x, y) and velocity (vx, vy)
  - No collision between joints (they can pass through each other)
  - Collision with ground only (y >= 0)
  - Ground collision includes normal force and friction
  
- **Muscles (Edges)**:
  - Spring-damper systems connecting two joints
  - Spring constant k (from settings)
  - Natural/resting length controlled by neural network
  - Force = -k * (current_length - resting_length)
  - Damping to prevent infinite oscillation

#### Physics Integration
- Use Verlet integration or RK4 for numerical stability
- Handle ground collisions with:
  - Normal force preventing penetration
  - Friction force opposing horizontal movement when in contact
  - Coefficient of friction from settings

### 2. Neural Network System

#### Architecture
- Inputs (per muscle):
  - Current muscle length
  - Current muscle resting length
  - (Total inputs = 2 * number of muscles)
  
- Hidden Layer:
  - Single hidden layer with H neurons (H = number of muscles * 2)
  - Tanh activation
  
- Outputs:
  - One output per muscle
  - Sigmoid activation ? [0, 1]
  - Mapped to [min_rest%, max_rest%] of initial muscle length
  - Example: If initial length = 50, min=50%, max=150%
    - Output 0 ? resting length = 25
    - Output 1 ? resting length = 75

#### Dynamic Topology Handling
When creature topology changes (add/remove muscle):
- Add/remove corresponding NN inputs and outputs
- Initialize new weights randomly [-1, 1]
- Preserve existing weights where possible

### 3. Genetic Algorithm

#### Population Management
- Fixed population size: 100 creatures
- Selection: Top 50% by fitness survive
- Reproduction: Each survivor creates 1 mutated offspring

#### Fitness Function
- Fitness = Final center of mass X position - Initial center of mass X position
- Center of mass = weighted average of joint positions
- Must handle negative fitness (moving backwards)

#### Mutation Operations
1. **Neural Network Weight Mutation**
   - For each weight: P(mutate) = nn_mutation_chance
   - If mutating: weight += normal(0, 0.1)
   
2. **Joint Position Mutation**
   - For each joint: P(mutate) = joint_mutation_chance
   - If mutating: position += normal(0, 5) pixels
   
3. **Add/Remove Joint Mutation**
   - P(add joint) = joint_add_remove_chance / 2
   - P(remove joint) = joint_add_remove_chance / 2
   - Constraints: min_joints <= num_joints <= max_joints
   - New joint: random position near existing structure
   - Remove: random joint (update connected muscles)
   
4. **Add/Remove Muscle Mutation**
   - P(add muscle) = muscle_add_remove_chance / 2
   - P(remove muscle) = muscle_add_remove_chance / 2
   - Add: connect two unconnected joints
   - Remove: random muscle

### 4. Creature Initialization

For first generation:
1. Random number of joints [min_joints, max_joints]
2. Random positions in spawn area (x: [0, 100], y: [50, 200])
3. Random muscle connections (ensure connected graph)
4. Random initial muscle lengths [min_length, max_length]
5. Random neural network weights [-1, 1]

### 5. API Specification
**This specification has been updated to match the frontend''s implementation and the primary `documentation.md` file.**

#### POST /api/evolution/run
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

#### GET /api/evolution/results/{runId}
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

### 6. Testing Requirements
Unit Tests

Physics calculations (spring forces, collisions, friction)
Neural network forward pass
Mutation operations
Fitness calculation

Integration Tests

Fitness Monotonicity: Best fitness in generation N+1 >= generation N
Ground Collision: No joint should ever have y < 0
Physics Conservation: Energy should dissipate (not increase) over time
Population Consistency: Always exactly 100 creatures
Topology Constraints: min_joints <= creature.joints <= max_joints
Neural Network Consistency: NN inputs/outputs match muscle count
Deterministic Replay: Same creature produces same trajectory
Mutation Bounds: All mutations respect configured limits

Performance Tests

Must simulate 100 creatures × 10 seconds in < 30 seconds
Memory usage should be stable across generations

### 7. Critical Implementation Details

Coordinate System: Y-up (ground at y=0, gravity pulls negative)
Units: Pixels for display, but use consistent physics units internally
Random Seed: Make simulations reproducible for testing
Muscle Ordering: Consistent ordering for NN input/output mapping
Graph Connectivity: Ensure creature remains single connected component
Numerical Stability: Handle edge cases (zero-length muscles, etc.)

This system should demonstrate emergent locomotion strategies through evolutionary pressure, with creatures learning to exploit the spring-muscle system for forward movement.
