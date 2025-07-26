# Testing Requirements

This document outlines the testing strategy to ensure the correctness, stability, and performance of the Darwinistic Evolution Simulator.

## 1. Unit Testing

Unit tests should focus on individual components in isolation.

-   **Mutation Functions**:
    -   Verify `nnWeightMutationChance` correctly mutates a percentage of weights.
    -   Verify `jointPositionMutationChance` correctly translates joint positions.
    -   Test `addRemoveJointMutationChance`:
        -   Ensure a joint is added correctly with a connecting muscle.
        -   Ensure a joint and its connected muscles are removed.
        -   Verify that the number of joints stays within `minJoints` and `maxJoints`.
    -   Test `addRemoveMuscleMutationChance`:
        -   Ensure a muscle is added between two valid, previously unconnected joints.
        -   Ensure a muscle can be removed without disconnecting the creature.
-   **Evolutionary Logic**:
    -   Test fitness calculation: Ensure it correctly identifies the max `x` of the center of mass.
    -   Test selection logic: Ensure the top 50% of creatures are correctly selected.
    -   Test reproduction: Ensure a parent is copied and the offspring is mutated.
-   **Neural Network**:
    -   Test the forward pass of the neural network with mock inputs to ensure outputs are generated for each muscle.

## 2. Integration Testing

Integration tests will verify the interactions between different parts of the system.

-   **Full Generational Flow**:
    -   Run a small simulation (e.g., 5 creatures, 2 generations).
    -   Assert that the second generation is composed of the top performers from the first, plus their mutated offspring.
-   **API Workflow**:
    -   Test the complete user flow: `POST /evolution/run` -> `GET /evolution/status/{runId}` (polling) -> `GET /evolution/results/{runId}`.
    -   Verify that a `continueFromLastRun: true` request correctly uses the cached population from the previous run.
-   **Data Integrity**:
    -   Ensure the `CreatureDataPayload` returned by the API matches the structure expected by the frontend (`Playback.tsx`, `Results.tsx`).
    -   Verify that all data (playback, fitness, connectivity) is sorted correctly by fitness.

## 3. Physics Stability Testing (CRITICAL)

This is the most critical area of testing due to the complexity of the physics engine.

-   **Ground Plane Collision**:
    -   **Scenario**: A creature is dropped from a height.
    -   **Expected**: The creature''s joints should collide with the ground plane (`y=400` in the frontend coordinate system) and bounce or rest on it, not pass through it.
-   **Energy Stability**:
    -   **Scenario**: Run a single, non-moving creature for an extended period (e.g., 5000 frames).
    -   **Expected**: The total kinetic energy of the system should decay and stabilize, not increase unboundedly (i.e., the creature should not ''explode'').
-   **Coordinate System Synchronization**:
    -   **Scenario**: Create a creature with a known initial position in the backend.
    -   **Expected**: The initial frame of the `playbackData` must show the creature at the exact corresponding position in the frontend''s coordinate system. The ground in the backend must be equivalent to `y=400` in the frontend canvas.
-   **Friction Test**:
    -   **Scenario**: Give a creature an initial horizontal velocity on the ground.
    -   **Expected**: The creature should slow down and eventually stop due to the `groundFriction` parameter.

## 4. API Endpoint Testing

Each API endpoint must be tested for various scenarios.

-   **`POST /evolution/run`**:
    -   **Success (200)**: With a valid `ApiRunRequest`.
    -   **Bad Request (400)**: With invalid `settings` (e.g., `minJoints` > `maxJoints`).
    -   **Bad Request (400)**: With `continueFromLastRun: true` when no previous run is cached.
-   **`GET /evolution/status/{runId}`**:
    -   **Success (200)**: For a valid `runId`.
    -   **Not Found (404)**: For an invalid or non-existent `runId`.
-   **`GET /evolution/results/{runId}`**:
    -   **Success (200)**: For a completed `runId`.
    -   **Accepted (202)**: If the run is still processing (or return a specific status).
    -   **Not Found (404)**: For an invalid or non-existent `runId`.

## 5. Performance Testing

-   **Benchmark**: The simulation of a full generation (100 creatures, 600 frames each) should complete within a target time (e.g., under 60 seconds on the target hardware).
-   **Concurrency**: The API should handle multiple simultaneous requests to `/run` without crashing or corrupting data (each run should be isolated).
