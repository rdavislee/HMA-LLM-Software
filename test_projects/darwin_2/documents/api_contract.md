# API Contract Specification

This document defines the RESTful API contract for the Darwinistic Evolution Simulator backend. The frontend will interact with these endpoints to run simulations and retrieve results.

## Base URL

All API endpoints are prefixed with `/api`.

## Standard Response Format

### Success Response
Successful responses will typically have a `2xx` status code and a JSON body relevant to the request.

### Error Response
Error responses will have a `4xx` or `5xx` status code and a JSON body with the following structure:

```json
{
  "error": "ERROR_CODE",
  "message": "A human-readable description of the error."
}
```

---

## Endpoints

### 1. Run Evolution Simulation

Starts a new evolution simulation or continues from the last cached generation.

- **Endpoint**: `POST /evolution/run`
- **Description**: Initiates a potentially long-running background task to simulate the specified number of generations. It should return a unique ID for the run immediately.
- **Request Body**:

```json
{
  "settings": { ... }, // The complete SimulationSettings object from the frontend
  "generations": 10,     // The number of generations to run
  "continueFromLastRun": false // Optional: true to use the cached generation as the starting point
}
```

- **Success Response (202 Accepted)**:

```json
{
  "runId": "a-unique-identifier-uuid",
  "status": "PROCESSING",
  "message": "Simulation run has been accepted and is now processing."
}
```

- **Error Responses**:
  - `422 Unprocessable Entity`: If `settings` are invalid or `generations` is not a positive integer.
  - `400 Bad Request`: If `continueFromLastRun` is `true` but there is no generation cached.
  - `429 Too Many Requests`: If the rate limit is exceeded.

---

### 2. Get Simulation Status

Polls for the status of an ongoing simulation.

- **Endpoint**: `GET /evolution/status/{runId}`
- **Description**: Allows the frontend to check the progress of a simulation without having to wait for the full results.
- **URL Parameters**:
  - `runId` (string): The unique identifier returned by the `/evolution/run` endpoint.
- **Success Response (200 OK)**:

```json
{
  "runId": "a-unique-identifier-uuid",
  "status": "PROCESSING" | "COMPLETED" | "FAILED",
  "progress": 0.7, // A float between 0.0 and 1.0 indicating completion percentage
  "currentGeneration": 7, // The current generation being processed
  "totalGenerations": 10
}
```

- **Error Responses**:
  - `404 Not Found`: If the `runId` does not correspond to any known simulation run.

---

### 3. Get Simulation Results

Retrieves the complete results of a finished simulation, including playback data.

- **Endpoint**: `GET /evolution/results/{runId}`
- **Description**: Fetches the detailed data required for the `/playback` and `/results` pages on the frontend.
- **URL Parameters**:
  - `runId` (string): The unique identifier for the run.
- **Success Response (200 OK)**: The body will be the `CreatureData` object, structured exactly as defined in `Playback.tsx`.

```json
{
  "playbackData": [ ... ],    // number[][][]: [creature][frame][joint][x,y]
  "fitnessScores": [ ... ],   // number[]
  "initialPositions": [ ... ],// number[][]: [creature][joint_x, joint_y, ...]
  "muscleConnectivity": [ ... ] // number[][][]: [creature][muscle][joint1_idx, joint2_idx]
}
```

- **Error Responses**:
  - `202 Accepted`: If the simulation is still processing (as a fallback if the frontend calls this endpoint before the status is `COMPLETED`). The body could contain status information.
  - `404 Not Found`: If the `runId` does not exist.
  - `500 Internal Server Error`: If the simulation run failed.
