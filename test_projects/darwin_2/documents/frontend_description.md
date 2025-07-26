# Frontend Description and Analysis

This document describes the provided React frontend, its user flow, and the resulting requirements for the backend API.

## 1. Technology Stack

- **Framework**: React 18 with TypeScript
- **UI Components**: `shadcn/ui` (as indicated by `components/ui` directory)
- **Routing**: `react-router-dom`
- **State Management**: Local component state (`useState`) and route state for passing data between pages.
- **API Calls**: Native `fetch` API.

## 2. Page and User Flow Analysis

The application consists of four main pages that define the user journey:

### 2.1. Settings Page (`/`)

- **Purpose**: The main entry point where users configure and start a simulation.
- **UI**: A form with numerous input fields for `SimulationSettings` and a field for the number of generations (`N`).
- **Actions**:
    - **"Run 1 Generation" / "Run N Generations"**: These buttons trigger the simulation.
- **Interaction Logic**:
    - Clicking a "Run" button **does not** directly call the API.
    - Instead, it navigates the user to the `/processing` page.
    - It passes the complete `settings` object and the number of `generations` to run via the router''s state.

### 2.2. Processing Page (`/processing`)

- **Purpose**: To initiate the backend simulation and provide visual feedback while it runs.
- **UI**: A loading screen showing the current generation being processed and a progress bar.
- **Interaction Logic**:
    1.  On load, it retrieves the `settings` and `generations` from the route state.
    2.  It makes a **`POST`** request to **`/api/evolution/run`** with the `settings` and `generations` in the request body.
    3.  It expects a JSON response containing a unique `runId`.
    4.  While waiting, it displays a mock progress animation. **(Note: A polling mechanism to a status endpoint is implied here for a real implementation but is not present in the provided code.)**
    5.  Once the (mock) processing is complete, it navigates to the `/playback` page, passing the `settings`, `generations`, and the `runId`.

### 2.3. Playback Page (`/playback`)

- **Purpose**: To visualize the movement of the best-performing creatures from the completed simulation.
- **UI**: A large canvas displaying one creature at a time, with controls to cycle through creatures.
- **Interaction Logic**:
    1.  On load, it retrieves the `runId` from the route state.
    2.  It makes a **`GET`** request to **`/api/evolution/results/{runId}`**.
    3.  It expects a large JSON payload (`CreatureData`) containing playback animation data, fitness scores, and creature structures.
    4.  It animates the creatures on the canvas, sorted from best to worst fitness.

### 2.4. Results Page (`/results`)

- **Purpose**: To display a summary of the entire generation and allow the user to continue the evolution.
- **UI**: A grid of 100 small canvases, each showing a static image of one creature from the final generation, ordered by fitness.
- **Actions**:
    - **"Run Next Generation" / "Run N More Generations"**: These buttons allow the user to continue the evolutionary process.
- **Interaction Logic**:
    - This page **does not** make an API call. It receives the `creatureData` directly from the `/playback` page via route state.
    - Clicking a "Run" button navigates the user back to the `/processing` page.
    - This flow implies that the backend must support **continuing a simulation from the last run**. The `POST /api/evolution/run` request will need to differentiate between a new run and a continued run.

## 3. Implied Backend Requirements

- **Stateless Continuation**: The backend must cache the state of the last generation to allow the "Run Next Generation" feature to work. It must be able to start a new simulation using the previous generation as a base.
- **Asynchronous Job Processing**: The `run` -> `processing` -> `results` flow is a classic asynchronous job pattern. The `POST /api/evolution/run` endpoint should start a background task and return a `runId` immediately.
- **Polling Endpoint**: A `GET /api/evolution/status/{runId}` endpoint is needed for the frontend to poll for progress and determine when the simulation is complete. This is not explicitly used in the demo code but is essential for a robust implementation.
- **Data Structure Adherence**: The `GET /api/evolution/results/{runId}` endpoint must return data in the exact `CreatureData` structure defined in `Playback.tsx`.
