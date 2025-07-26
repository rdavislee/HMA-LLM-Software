# Error Scenarios and Handling

This document specifies potential failure modes and the expected behavior of the backend API in each case.

## 1. API Input Validation Errors (HTTP 400/422)

These errors occur when the client sends a request with invalid or malformed data. The response should include a clear error message indicating which field is problematic.

| Scenario                                          | Endpoint                 | Request Body / Params                                       | Response Code | Response Body Example                                                              |
| ------------------------------------------------- | ------------------------ | ----------------------------------------------------------- | ------------- | ---------------------------------------------------------------------------------- |
| Invalid `settings` values                         | `POST /evolution/run`    | `settings.minJoints > settings.maxJoints`                   | 422           | `{\"error\": \"VALIDATION_ERROR\", \"message\": \"minJoints cannot be greater than maxJoints.\"}` |
| Negative or zero `generations`                    | `POST /evolution/run`    | `generations: -5`                                           | 422           | `{\"error\": \"VALIDATION_ERROR\", \"message\": \"generations must be a positive integer.\"}` |
| Missing `settings` object                         | `POST /evolution/run`    | Request body is empty or missing `settings` field.          | 422           | `{\"error\": \"VALIDATION_ERROR\", \"message\": \"settings field is required.\"}`           |
| Attempt to continue with no cached generation     | `POST /evolution/run`    | `continueFromLastRun: true` when server cache is empty.     | 400           | `{\"error\": \"NO_CACHED_RUN\", \"message\": \"No previous generation available to continue from.\"}` |

## 2. Resource Not Found Errors (HTTP 404)

These errors occur when the client requests a resource that does not exist.

| Scenario                                          | Endpoint                          | Request Body / Params         | Response Code | Response Body Example                                                              |
| ------------------------------------------------- | --------------------------------- | ----------------------------- | ------------- | ---------------------------------------------------------------------------------- |
| Requesting status of a non-existent run           | `GET /evolution/status/{runId}`   | `runId` does not exist.       | 404           | `{\"error\": \"RUN_NOT_FOUND\", \"message\": \"Simulation run with the specified ID was not found.\"}` |
| Requesting results of a non-existent run          | `GET /evolution/results/{runId}`  | `runId` does not exist.       | 404           | `{\"error\": \"RUN_NOT_FOUND\", \"message\": \"Simulation run with the specified ID was not found.\"}` |

## 3. Asynchronous Task Status

Handling requests for results of a run that is still in progress.

| Scenario                                          | Endpoint                          | Request Body / Params         | Response Code | Response Body Example                                                              |
| ------------------------------------------------- | --------------------------------- | ----------------------------- | ------------- | ---------------------------------------------------------------------------------- |
| Requesting results of an in-progress run          | `GET /evolution/results/{runId}`  | `runId` exists but is not done. | 202           | `{\"status\": \"PROCESSING\", \"progress\": 0.75, \"message\": \"Simulation is still running.\"}` |

## 4. Internal Server Errors (HTTP 500)

These are unexpected errors that occur on the server side. The response should be generic to avoid leaking implementation details, but a correlation ID for logging is recommended.

| Scenario                                          | Trigger                               | Response Code | Response Body Example                                                                |
| ------------------------------------------------- | ------------------------------------- | ------------- | ------------------------------------------------------------------------------------ |
| Physics simulation instability (e.g., NaN values) | A bug in the physics engine.          | 500           | `{\"error\": \"SIMULATION_FAILURE\", \"message\": \"An unexpected error occurred during the simulation. Run ID: [uuid]\"}` |
| Out of memory during simulation                   | A very large or long simulation.      | 500           | `{\"error\": \"INTERNAL_SERVER_ERROR\", \"message\": \"The server encountered an unexpected condition. Run ID: [uuid]\"}` |
| Unhandled exception in any part of the code       | Any unexpected bug.                   | 500           | `{\"error\": \"INTERNAL_SERVER_ERROR\", \"message\": \"The server encountered an unexpected condition. Run ID: [uuid]\"}` |
