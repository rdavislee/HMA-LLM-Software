# Business Logic and Algorithms

This document details the core logic for the evolution simulation, including the physics engine, evolutionary algorithm, and neural network control.

---

## 1. Main Simulation Loop

The simulation proceeds in discrete generations. For each generation, the following steps are executed:

1.  **Initialization**: A population of 100 creatures is created. For the first generation, this is random. For subsequent generations, this is based on the output of the evolutionary algorithm from the previous generation.
2.  **Parallel Simulation**: Each of the 100 creatures is simulated independently in its own physics environment for a fixed duration (e.g., 10 seconds or 600 physics frames).
3.  **Fitness Calculation**: After each creature''s simulation is complete, its fitness is calculated. Fitness is defined as the maximum horizontal (x-axis) distance traveled to the right by the creature''s center of mass.
4.  **Selection & Reproduction**: The creatures are ranked by their fitness scores. The evolutionary algorithm is applied to produce the 100 creatures for the next generation.
5.  **Data Aggregation**: Playback data (joint positions per frame) and final results are collected for the generation.
6.  **Loop or Complete**: If more generations are requested, the loop continues. Otherwise, the final results are stored for retrieval, and the state of the final generation is cached.

---

## 2. Evolutionary Algorithm

This algorithm is applied after all creatures in a generation have been simulated and their fitness has been calculated.

1.  **Selection**: The 100 creatures are sorted by fitness in descending order.
    - The **Top 50** creatures are selected to be the ''survivors''.
    - The Bottom 50 creatures are discarded.

2.  **Reproduction (Asexual with Mutation)**:
    - Each of the 50 survivor creatures produces exactly one offspring, creating a new population of 50 children.
    - The offspring is initially an identical clone of its parent (same joints, muscles, and neural network weights).

3.  **Mutation**:
    - A mutation function is applied to each of the 50 offspring. The function applies several types of mutations based on probabilities defined in `SimulationSettings`:
      - **NN Weight Mutation**: Iterate through every weight and bias in the offspring''s neural network. For each, there is a `nnWeightMutationChance` to perturb its value slightly (e.g., by a small random amount).
      - **Joint Position Mutation**: There is a `jointPositionMutationChance` for the entire creature to undergo this mutation. If it occurs, one randomly selected joint has its initial position translated by a small random vector.
      - **Add/Remove Joint Mutation**: There is an `addRemoveJointMutationChance`. If triggered, the system will either add a new joint (and connect it with a new muscle to a nearby existing joint) or remove a random joint (and any attached muscles). The number of joints must stay within `minJoints` and `maxJoints`.
      - **Add/Remove Muscle Mutation**: There is an `addRemoveMuscleMutationChance`. If triggered, the system will either add a new muscle between two existing, non-connected joints or remove a random existing muscle.

4.  **New Population Assembly**: The new generation consists of the 50 original survivors and their 50 mutated offspring, totaling 100 creatures.

---

## 3. Physics Simulation

Each creature is simulated in a 2D physics world.

-   **Creature Model**: Creatures are represented as a collection of point masses (`Joints`) connected by springs (`Muscles`).
-   **Ground**: A static, infinite horizontal plane exists at a fixed Y-coordinate (e.g., y=400, to match the frontend). It has a friction property (`groundFriction`).
-   **Simulation Step**: The simulation advances in discrete time steps (e.g., 1/60th of a second).
    1.  **NN Brain Tick**: The creature''s neural network is activated. Inputs to the NN should include time, and could include proprioceptive data like current joint positions/velocities and muscle lengths.
    2.  **Muscle Control**: The NN''s outputs are used to set the `current_rest_length` for each muscle, within the bounds of `minSpringRest` and `maxSpringRest` percentage of the muscle''s initial length.
    3.  **Force Calculation**: Calculate forces on each joint (spring forces from muscles, gravity, ground collision/friction forces).
    4.  **Integration**: Use an integration method (e.g., Verlet or Euler) to update the position and velocity of each joint based on the calculated forces and its `jointWeight`.
    5.  **Data Recording**: Store the positions of all joints for the current frame. This becomes the `playbackData`.

---

## 4. Neural Network (Brain)

-   **Architecture**: A simple feed-forward neural network. The exact topology (number of layers, neurons per layer) can be fixed or could itself be subject to mutation.
-   **Inputs**: A minimal set of inputs should include a sine wave based on the current time `sin(time * frequency)` to provide a clock signal, allowing for rhythmic movements.
-   **Outputs**: The number of output neurons must equal the number of muscles in the creature. Each output value (typically passed through a sigmoid or tanh function to be in a range like [0, 1] or [-1, 1]) is mapped to the target `current_rest_length` for its corresponding muscle.
