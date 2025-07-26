# API Specification

This document provides the definitive specification for the Evolution Simulator backend API. The frontend relies on these exact contracts.

## Endpoints

### `POST /api/evolution/run`

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

### `GET /api/evolution/results/{runId}`

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
