# Darwinistic Evolution Simulator - Backend

This is the backend for the Darwinistic Evolution Simulator, a FastAPI application that runs evolutionary simulations.

## Project Structure

- `src/`: Main application source code.
  - `api/`: FastAPI routers and API-level logic.
  - `core/`: Core application setup (config, DI container).
  - `models/`: Pydantic data models for creatures, simulations, etc.
  - `services/`: Core business logic (physics, evolution).
  - `mocks/`: Mock implementations for parallel development and testing.
  - `utils/`: Shared utilities like logging.
- `integration/`: End-to-end integration tests.
- `documents/`: Project planning and design documents.

## Setup and Installation

1.  **Prerequisites**: Python 3.11+
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    Or using the Makefile:
    ```bash
    make install
    ```

## Running the Application

To run the development server with live reloading:
```bash
make run
```
The API will be available at `http://localhost:8000`.

## Running Tests

To run the complete test suite and see a coverage report:
```bash
make test
```
The tests are configured in `pytest.ini` to enforce a minimum of 80% code coverage.

## Code Quality

This project uses `ruff` for linting and formatting.

- **Check for linting errors**:
  ```bash
  make lint
  ```
- **Automatically format the code**:
  ```bash
  make format
  ```
