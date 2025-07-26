# Backend Development Plan: Darwinistic Evolution Simulator

## 1. Overview

This document outlines a phased, parallel development strategy for the backend of the Darwinistic Evolution Simulator. The primary goal is to structure the work into independent tracks to maximize development speed and minimize conflicts. The architecture is built around a clean separation of concerns: Models, Core Services, and the API Layer.

## 2. Concurrent Development Tracks

The project will be developed across four distinct, parallelizable phases.

### Phase 1: Foundational Layer (Data Models & Configuration)

**Goal:** Define all core data structures and application settings. This phase has no internal dependencies and can be fully parallelized.

*   **Track 1A: Creature & Physics Models**
    *   **Files:** `src/models/creature.py`, `src/models/test_creature.py`
    *   **Task:** Implement the `Node`, `Muscle`, and `Creature` data classes. These will represent the physical components of a creature.
*   **Track 1B: Simulation & State Models**
    *   **Files:** `src/models/simulation.py`, `src/models/test_simulation.py`
    *   **Task:** Implement `SimulationSettings`, `SimulationRequest`, `GenerationResult`, and `SimulationState` to manage simulation parameters and results.
*   **Track 1C: Configuration**
    *   **Files:** `src/core/config.py`, `src/core/test_config.py`
    *   **Task:** Finalize all environment variables and application settings using `pydantic-settings`. Ensure all settings are documented in `.env.example`.

### Phase 2: Core Logic (Physics & Evolution Services)

**Goal:** Implement the complex, computationally-intensive simulation logic. These two tracks are the core of the application and can be developed independently once Phase 1 is complete.

*   **Track 2A: Physics Service**
    *   **Files:** `src/services/physics_service.py`, `src/services/test_physics_service.py`
    *   **Task:** Implement the `PhysicsService`. This service will take a single `Creature` and `SimulationSettings`, use `pymunk` to run a 2D physics simulation, and return the creature's fitness score (e.g., distance traveled). An Abstract Base Class `IPhysicsService` should be defined.
*   **Track 2B: Evolution Service**
    *   **Files:** `src/services/evolution_service.py`, `src/services/test_evolution_service.py`
    *   **Task:** Implement the `EvolutionService`. This service will take a population of `Creature` instances with their fitness scores, perform selection (e.g., top 50%), and generate a new population through mutation and reproduction. An Abstract Base Class `IEvolutionService` should be defined.

### Phase 3: Application Layer (Orchestration & API)

**Goal:** Integrate the core services and expose the simulation functionality through the API. This work can begin in parallel with Phase 2 by using mock implementations of the services.

*   **Track 3A: Simulation Orchestration**
    *   **Files:** `src/services/simulation_manager.py`, `src/services/test_simulation_manager.py`
    *   **Task:** Enhance the `SimulationManager`. It will orchestrate the entire multi-generational simulation by repeatedly calling the `PhysicsService` to evaluate a generation and the `EvolutionService` to create the next one. It will manage job state (running, completed, error).
*   **Track 3B: API Enhancements**
    *   **Files:** `src/api/simulation_router.py`, `src/api/test_simulation_router.py`
    *   **Task:** Implement the remaining API endpoints defined in `api_contract.md`, such as `/continue` (using the in-memory cache) and `/results/{job_id}` for fetching detailed generation data.

### Phase 4: Integration and Refinement

**Goal:** Ensure all components function correctly together and refine the application.

*   **Track 4A: Full E2E Testing**
    *   **Files:** `integration/test_simulation_flow.py`
    *   **Task:** Create comprehensive integration tests that simulate a user's entire journey: starting a simulation, polling for status, and retrieving final results.
*   **Track 4B: Technical Debt & Refinement**
    *   **Task:** Address the `DeprecationWarning` for `@app.on_event` by migrating to the recommended `lifespan` context manager in `src/main.py`. This improves compatibility with modern FastAPI.
    *   **Task:** Improve test coverage across the application to meet the 80% target.

## 3. Mocking Strategy for Parallel Development

To unblock Phase 3 development, mock implementations of the core services will be used.

1.  **Define Interfaces:** Create Abstract Base Classes (ABCs) in `src/services/` for `IPhysicsService` and `IEvolutionService`.
2.  **Create Mocks:** Implement simple mock versions in `src/mocks/` (e.g., `mock_physics_service.py`) that return predictable data.
3.  **Dependency Injection:** The `SimulationManager` and `APIRouter` will depend on the ABCs, not the concrete classes. The DI container in `src/core/container.py` will provide either the real or mock implementations, allowing the application layer to be developed and tested before the core services are complete.

## Ongoing Initialisation

Human goal: this project just finished phase 2. All you need to do is read the documents files, read the frontend files which use the api, and finish for phase 3.

