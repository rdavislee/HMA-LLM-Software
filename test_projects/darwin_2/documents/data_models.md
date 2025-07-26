# Data Models Specification

This document defines the core data structures used by the backend system. These models represent the configuration, state, and results of the evolution simulation.

---

## 1. Simulation Configuration Models

These models are received from the frontend to configure a simulation run.

### `SimulationSettings`

This object contains all user-configurable parameters for the physics and evolution engine. It directly corresponds to the `SimulationSettings` interface in `Settings.tsx`.

```typescript
interface SimulationSettings {
  // Spring/Muscle properties
  minSpringRest: number;            // Minimum resting length of a spring as a percentage of initial length.
  maxSpringRest: number;            // Maximum resting length of a spring as a percentage of initial length.
  minInitialSpringLength: number;   // Minimum length for newly created springs.
  maxInitialSpringLength: number;   // Maximum length for newly created springs.
  springStiffness: number;          // The stiffness constant for all springs.

  // Joint/Node properties
  jointWeight: number;              // The mass of each joint.
  minJoints: number;                // Minimum number of joints for a new creature.
  maxJoints: number;                // Maximum number of joints for a new creature.

  // Physics properties
  groundFriction: number;           // The friction coefficient of the ground plane.

  // Mutation probabilities (as percentages)
  nnWeightMutationChance: number;       // The chance for a single neural network weight to be mutated.
  jointPositionMutationChance: number;  // The chance for a joint''s position to be slightly translated.
  addRemoveJointMutationChance: number; // The chance to add or remove a joint.
  addRemoveMuscleMutationChance: number;// The chance to add or remove a muscle.
}
```

---

## 2. Core Simulation Models

These are the internal representations of the entities within the physics and evolution simulation.

### `Joint` (Node)

Represents a point mass in the creature.

```python
class Joint:
    id: int
    position: tuple[float, float]  # (x, y) coordinates
    velocity: tuple[float, float]  # (vx, vy)
```

### `Muscle` (Spring)

Represents a spring connecting two joints.

```python
class Muscle:
    id: int
    joint1_id: int              # ID of the first connected joint
    joint2_id: int              # ID of the second connected joint
    initial_length: float       # The original length when created
    current_rest_length: float  # The target resting length, controlled by the NN
```

### `NeuralNetwork`

The brain of a creature. It takes environmental inputs and outputs muscle control signals.

```python
class NeuralNetwork:
    # Inputs could include: joint positions/velocities, ground contact, time
    # Outputs: a value for each muscle to set its target resting length
    weights: list[list[float]] # A simple representation, e.g., a list of weight matrices for each layer
    biases: list[list[float]]  # A list of bias vectors for each layer
```

### `Creature`

The complete representation of a single evolving entity.

```python
class Creature:
    id: int
    joints: list[Joint]
    muscles: list[Muscle]
    brain: NeuralNetwork
    fitness: float = 0.0 # Calculated after simulation, measures distance traveled right
```

### `Generation`

A collection of creatures that are simulated together.

```python
class Generation:
    generation_number: int
    creatures: list[Creature] # Population size is fixed (e.g., 100)
```

---

## 3. API and Job Management Models

These models are used for managing the simulation lifecycle via the API.

### `SimulationRun`

An internal object to track the state of a simulation job.

```python
class SimulationRun:
    run_id: str
    status: str # e.g., "PROCESSING", "COMPLETED", "FAILED"
    progress: float
    current_generation: int
    total_generations: int
    results: CreatureData | None # Populated when status is "COMPLETED"
    last_generation_state: Generation | None # Cached for the `continue` functionality
```

### `CreatureData` (API Response Model)

This is the data structure returned by the `GET /evolution/results/{runId}` endpoint. It must match the frontend''s expectation from `Playback.tsx`.

```typescript
interface CreatureData {
  // Playback data: A 3D array for animating creature movement.
  // Format: [creature_index][frame_index][joint_data]
  // joint_data is a flat array: [joint0_x, joint0_y, joint1_x, joint1_y, ...]
  playbackData: number[][][];

  // Fitness scores for each creature, sorted from best to worst.
  fitnessScores: number[];

  // The initial (frame 0) positions of all joints for each creature.
  // Format: [creature_index][joint_data]
  initialPositions: number[][];

  // The connectivity map for muscles.
  // Format: [creature_index][muscle_index][joint1_index, joint2_index]
  muscleConnectivity: number[][][];
}
```
