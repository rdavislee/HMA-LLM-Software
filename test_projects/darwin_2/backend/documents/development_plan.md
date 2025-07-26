# Development Plan: Darwinistic Evolution Simulator

## 1. Overview
This plan outlines a phased, concurrent development strategy to build the backend. The architecture is designed to maximize parallel work by separating concerns into distinct modules with clear interfaces (Pydantic models).

## 2. Concurrent Development Tracks

### Track 1: Foundational Models & Configuration (Can start immediately)
*   **Agent(s)**: 1
*   **Scope**:
    *   Define all Pydantic models in `src/models/` based on `documents/data_models.md`.
    *   Implement the core configuration loading in `src/core/config.py`.
    *   Write comprehensive unit tests for all models and configuration logic.
*   **Outcome**: A fully defined and tested data layer.

### Track 2: Physics Simulation Service (Can start immediately)
*   **Agent(s)**: 1-2
*   **Scope**:
    *   Implement the core physics engine logic within `src/services/physics_service.py` using `pymunk`.
    *   Write unit and integration tests to verify physics accuracy.
*   **Outcome**: A standalone, testable physics simulation module.

### Track 3: Evolutionary Algorithm Service (Depends on Track 1 Models)
*   **Agent(s)**: 1-2
*   **Scope**:
    *   Implement the evolutionary logic in `src/services/evolution_service.py` (selection, reproduction, mutation).
    *   Write unit tests for each part of the evolutionary cycle.
*   **Outcome**: A module capable of evolving a population of creatures.

### Track 4: API Layer & Application Assembly (Depends on Service Interfaces)
*   **Agent(s)**: 1
*   **Scope**:
    *   Develop FastAPI routers in `src/api/` using mock services initially.
    *   Integrate real services as they become available.
    *   Write API-level integration tests using `httpx`.
*   **Outcome**: A functional API that can be tested against the frontend.

## 3. Mocking Strategy
- The API team (Track 4) will use mock service classes that return hardcoded Pydantic model objects, allowing frontend integration to begin immediately.

## 4. Integration & Testing Milestones
1.  **M1**: All models (Track 1) are defined and tested.
2.  **M2**: API (Track 4) is functional with mock services.
3.  **M3**: Physics service (Track 2) is integrated.
4.  **M4**: Evolution service (Track 3) is integrated.
5.  **M5**: Full end-to-end tests passing.
