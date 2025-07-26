# Darwin Evolution Simulator

This project is the backend for a 2D physics-based evolution simulator. Creatures, composed of joints (masses) and muscles (springs) controlled by a neural network, evolve over generations to improve their locomotion.

## Core Functionality
- Physics Simulation: A custom 2D physics engine using Verlet integration simulates creature movement.
- Genetic Algorithm: Creatures evolve through selection, mutation, and reproduction.
- Neural Network Control: Each creature's muscles are controlled by its own neural network "brain".
- REST API: A FastAPI server provides endpoints for a frontend to run simulations and visualize results.

## Project Structure
- `src/`: Contains all the Python source code for the backend.
- `documents/`: Contains detailed specification and requirements documents.
- `frontend/`: Contains the pre-built React frontend for visualization.
- `tests/`: This project follows an adjacent testing pattern. Tests are located next to the implementation files (e.g., `src/physics/physics_engine.py` and `src/physics/physics_engine_test.py`).

## Getting Started
1. Set up the environment:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    pip install -r requirements.txt
    ```
2. Run tests:
    ```bash
    python -m pytest -v
    ```
3. Run the application:
    ```bash
    uvicorn src/main:app --reload
    ```
The API will be available at `http://127.0.000:8000`.

## Subdirectories
- src/ - [BEGUN] Neural network bug fixed. Physics ground penetration issue identified as Pymunk limitation requiring higher-level review. Genetic algorithm blocked awaiting `clone()` method in creature module.
- documents/ - [FINISHED] Contains detailed specification and requirements documents.
- frontend/ - [FINISHED] Frontend React application; 'runId' extraction and navigation logic updated. Requires human verification.
- tests/ - [FINISHED] Contains all project tests.
- scratch_pads/ - [NOT STARTED] Temporary development scratch pads.