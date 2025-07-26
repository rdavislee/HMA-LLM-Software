import pytest
import httpx
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio
from fastapi import BackgroundTasks
import uuid
import random

# Import the FastAPI app instance from main.py
from src.main import app
# Import the cache from endpoints.py to manipulate it directly for GET tests
from src.api.endpoints import _simulation_results_cache, _run_simulation_and_store_results

# Fixture to create an AsyncClient for testing
@pytest.fixture(scope="module")
async def async_client():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        yield client

# Fixture to clear the simulation results cache before each test
@pytest.fixture(autouse=True)
def clear_cache():
    _simulation_results_cache.clear()
    yield
    _simulation_results_cache.clear() # Ensure clean state after test as well
@pytest.fixture(autouse=True)
def mock_run_simulation():
    '''
    Fixture to mock src.orchestrator.orchestrator.run_simulation to prevent actual long-running simulations.
    '''
    mock_results = {
        "playbackData": [[[1.0, 2.0]]],
        "fitnessScores": [10.0],
        "initialPositions": [[1.0, 2.0]],
        "muscleConnectivity": [[[0, 1]]]
    }
    with patch("src.orchestrator.orchestrator.run_simulation", new_callable=AsyncMock) as mock:
        mock.return_value = mock_results
        yield mock

@pytest.fixture(autouse=True)
def mock_run_simulation_and_store_results_background_task(mock_run_simulation):
    '''
    Fixture to mock src.api.endpoints._run_simulation_and_store_results
    to immediately set the cache with mocked results from mock_run_simulation.
    This prevents actual background task execution during tests.
    '''
    async def mock_task(run_id, settings, generations):
        # Directly set the cache with the results that mock_run_simulation would return
        # The mock_run_simulation fixture's return_value is the mock_results dict
        mock_results = mock_run_simulation.return_value
        _simulation_results_cache[run_id] = mock_results

    with patch("src.api.endpoints._run_simulation_and_store_results", new_callable=AsyncMock) as mock:
        mock.side_effect = mock_task
        yield mock



# Mock data for valid settings
VALID_SETTINGS = {
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
    "addRemoveMuscleMutationChance": 5,
    "orchestratorTestMode": None
}

# --- POST /api/evolution/run Tests ---

# Partition: Valid Requests (11 tests)
async def test_post_evolution_run_valid_request(async_client):
    '''
    Test valid request body and successful response (status 202, runId in response).
    Mock src.orchestrator.orchestrator.run_simulation and explicitly handle BackgroundTasks.
    '''
    request_body = {
        "settings": VALID_SETTINGS,
        "generations": 10
    }

    mock_orchestrator_results = {
        "playbackData": [[[1.0, 2.0]]],
        "fitnessScores": [10.0],
        "initialPositions": [[1.0, 2.0]],
        "muscleConnectivity": [[[0, 1]]]
    }
    
    with patch("src.api.endpoints._run_simulation_and_store_results", new_callable=AsyncMock) as mock_store_results:
        completion_future = asyncio.Future()
        mock_store_results.return_value = completion_future

        response = await async_client.post("/api/evolution/run", json=request_body)

        assert response.status_code == 202
        response_data = response.json()
        assert "runId" in response_data
        run_id = response_data["runId"]
        assert isinstance(run_id, str)
        assert uuid.UUID(run_id) # Check if it's a valid UUID

        cached_item = _simulation_results_cache.get(run_id)
        assert cached_item == {"status": "in_progress"}

        in_progress_response = await async_client.get(f"/api/evolution/results/{run_id}")
        assert in_progress_response.status_code == 202
        assert in_progress_response.json()["detail"] == "Simulation still in progress."
        
        mock_store_results.assert_called_once()
        called_run_id, called_settings, called_generations = mock_store_results.call_args[0]
        assert called_run_id == run_id
        assert called_settings == VALID_SETTINGS
        assert called_generations == 10

        completion_future.set_result(None)
        _simulation_results_cache[run_id] = mock_orchestrator_results
        assert _simulation_results_cache.get(run_id) == mock_orchestrator_results

async def test_post_evolution_run_valid_generations_one(async_client):
    '''Test valid request body: generations is 1.'''
    request_body = {
        "settings": VALID_SETTINGS,
        "generations": 1
    }
    response = await async_client.post("/api/evolution/run", json=request_body)
    assert response.status_code == 202

async def test_post_evolution_run_valid_generations_large_number(async_client):
    '''Test valid request body: generations is a large number.'''
    request_body = {
        "settings": VALID_SETTINGS,
        "generations": 100000
    }
    response = await async_client.post("/api/evolution/run", json=request_body)
    assert response.status_code == 202

async def test_post_evolution_run_settings_minSpringRest_boundary_min_valid(async_client):
    '''Test valid request body: minSpringRest at its minimum boundary (50.0).'''
    valid_settings = VALID_SETTINGS.copy()
    valid_settings["minSpringRest"] = 50.0
    response = await async_client.post("/api/evolution/run", json={"settings": valid_settings, "generations": 10})
    assert response.status_code == 202

async def test_post_evolution_run_settings_maxSpringRest_boundary_max_valid(async_client):
    '''Test valid request body: maxSpringRest at its maximum boundary (150.0).'''
    valid_settings = VALID_SETTINGS.copy()
    valid_settings["maxSpringRest"] = 150.0
    response = await async_client.post("/api/evolution/run", json={"settings": valid_settings, "generations": 10})
    assert response.status_code == 202

async def test_post_evolution_run_settings_minInitialSpringLength_boundary_min_valid(async_client):
    '''Test valid request body: minInitialSpringLength at its minimum boundary (30.0).'''
    valid_settings = VALID_SETTINGS.copy()
    valid_settings["minInitialSpringLength"] = 30.0
    response = await async_client.post("/api/evolution/run", json={"settings": valid_settings, "generations": 10})
    assert response.status_code == 202

async def test_post_evolution_run_settings_maxInitialSpringLength_boundary_max_valid(async_client):
    '''Test valid request body: maxInitialSpringLength at its maximum boundary (70.0).'''
    valid_settings = VALID_SETTINGS.copy()
    valid_settings["maxInitialSpringLength"] = 70.0
    response = await async_client.post("/api/evolution/run", json={"settings": valid_settings, "generations": 10})
    assert response.status_code == 202

async def test_post_evolution_run_settings_minJoints_boundary_min_valid(async_client):
    '''Test valid request body: minJoints at its minimum boundary (3).'''
    valid_settings = VALID_SETTINGS.copy()
    valid_settings["minJoints"] = 3
    response = await async_client.post("/api/evolution/run", json={"settings": valid_settings, "generations": 10})
    assert response.status_code == 202

async def test_post_evolution_run_settings_maxJoints_boundary_max_valid(async_client):
    '''Test valid request body: maxJoints at its maximum boundary (8).'''
    valid_settings = VALID_SETTINGS.copy()
    valid_settings["maxJoints"] = 8
    response = await async_client.post("/api/evolution/run", json={"settings": valid_settings, "generations": 10})
    assert response.status_code == 202

async def test_post_evolution_run_settings_jointWeight_large_positive(async_client):
    '''Test valid request body: jointWeight at a large positive value.'''
    valid_settings = VALID_SETTINGS.copy()
    valid_settings["jointWeight"] = 1000.0
    response = await async_client.post("/api/evolution/run", json={"settings": valid_settings, "generations": 10})
    assert response.status_code == 202

async def test_post_evolution_run_settings_springStiffness_large_positive(async_client):
    '''Test valid request body: springStiffness at a large positive value.'''
    valid_settings = VALID_SETTINGS.copy()
    valid_settings["springStiffness"] = 10000.0
    response = await async_client.post("/api/evolution/run", json={"settings": valid_settings, "generations": 10})
    assert response.status_code == 202

async def test_post_evolution_run_settings_all_settings_mid_range_valid(async_client):
    '''Test valid request body: all settings at typical mid-range values.'''
    mid_range_settings = {
        "minSpringRest": 75.0,
        "maxSpringRest": 125.0,
        "minInitialSpringLength": 40.0,
        "maxInitialSpringLength": 60.0,
        "groundFriction": 0.75,
        "jointWeight": 5.0,
        "minJoints": 4,
        "maxJoints": 7,
        "springStiffness": 500.0,
        "nnWeightMutationChance": 50,
        "jointPositionMutationChance": 25,
        "addRemoveJointMutationChance": 10,
        "addRemoveMuscleMutationChance": 15
    }
    response = await async_client.post("/api/evolution/run", json={"settings": mid_range_settings, "generations": 50})
    assert response.status_code == 202


# Partition: Invalid Generations (4 tests)
async def test_post_evolution_run_invalid_generations_type(async_client):
    '''Test invalid request body: generations with wrong type.'''
    request_body = {
        "settings": VALID_SETTINGS,
        "generations": "not_an_int" # Invalid type
    }
    response = await async_client.post("/api/evolution/run", json=request_body)
    assert response.status_code == 422
    assert "detail" in response.json()
    assert "valid integer" in response.json()["detail"][0]["msg"]

async def test_post_evolution_run_invalid_generations_zero(async_client):
    '''Test invalid request body: generations is zero.'''
    request_body = {
        "settings": VALID_SETTINGS,
        "generations": 0
    }
    response = await async_client.post("/api/evolution/run", json=request_body)
    assert response.status_code == 422
    assert "detail" in response.json()
    assert "greater than 0" in response.json()["detail"][0]["msg"]

async def test_post_evolution_run_invalid_generations_negative(async_client):
    '''Test invalid request body: generations is negative.'''
    request_body = {
        "settings": VALID_SETTINGS,
        "generations": -5
    }
    response = await async_client.post("/api/evolution/run", json=request_body)
    assert response.status_code == 422
    assert "detail" in response.json()
    assert "greater than 0" in response.json()["detail"][0]["msg"]

async def test_post_evolution_run_missing_generations(async_client):
    '''Test invalid request body: missing generations field.'''
    request_body = {
        "settings": VALID_SETTINGS,
        # "generations": 10 # Missing
    }
    response = await async_client.post("/api/evolution/run", json=request_body)
    assert response.status_code == 422
    assert "detail" in response.json()
    assert "Field required" in response.json()["detail"][0]["msg"]

# Partition: Invalid Settings (Type, Range, Missing) (27 tests)
async def test_post_evolution_run_invalid_settings_field(async_client):
    '''Test invalid request body: settings field with wrong type (e.g., float expected, string provided).'''
    invalid_settings = VALID_SETTINGS.copy()
    invalid_settings["minSpringRest"] = "not_a_float" # Invalid type
    request_body = {
        "settings": invalid_settings,
        "generations": 10
    }
    response = await async_client.post("/api/evolution/run", json=request_body)
    assert response.status_code == 422
    assert "detail" in response.json()
    assert "valid number" in response.json()["detail"][0]["msg"]

async def test_post_evolution_run_extra_field_in_settings(async_client):
    '''Test invalid request body: extra field in settings.'''
    extra_settings = VALID_SETTINGS.copy()
    extra_settings["extraField"] = 123 # Extra field
    request_body = {
        "settings": extra_settings,
        "generations": 10
    }
    response = await async_client.post("/api/evolution/run", json=request_body)
    assert response.status_code == 422
    assert "detail" in response.json()
    assert "Extra inputs are not permitted" in response.json()["detail"][0]["msg"]

async def test_post_evolution_run_missing_settings(async_client):
    '''Test invalid request body: missing settings field.'''
    request_body = {
        "generations": 10
    }
    response = await async_client.post("/api/evolution/run", json=request_body)
    assert response.status_code == 422
    assert "detail" in response.json()
    assert "Field required" in response.json()["detail"][0]["msg"]

async def test_post_evolution_run_settings_minSpringRest_out_of_range(async_client):
    '''Test invalid request body: minSpringRest too low or high.'''
    # Too low
    invalid_settings_low = VALID_SETTINGS.copy()
    invalid_settings_low["minSpringRest"] = 49.9
    response_low = await async_client.post("/api/evolution/run", json={"settings": invalid_settings_low, "generations": 10})
    assert response_low.status_code == 422
    assert "greater than or equal to 50" in response_low.json()["detail"][0]["msg"]

    # Too high
    invalid_settings_high = VALID_SETTINGS.copy()
    invalid_settings_high["minSpringRest"] = 150.1
    response_high = await async_client.post("/api/evolution/run", json={"settings": invalid_settings_high, "generations": 10})
    assert response_high.status_code == 422
    assert "less than or equal to 150" in response_high.json()["detail"][0]["msg"]

async def test_post_evolution_run_settings_maxSpringRest_out_of_range(async_client):
    '''Test invalid request body: maxSpringRest too low or high.'''
    # Too low
    invalid_settings_low = VALID_SETTINGS.copy()
    invalid_settings_low["maxSpringRest"] = 49.9
    response_low = await async_client.post("/api/evolution/run", json={"settings": invalid_settings_low, "generations": 10})
    assert response_low.status_code == 422
    assert "greater than or equal to 50" in response_low.json()["detail"][0]["msg"]

    # Too high
    invalid_settings_high = VALID_SETTINGS.copy()
    invalid_settings_high["maxSpringRest"] = 150.1
    response_high = await async_client.post("/api/evolution/run", json={"settings": invalid_settings_high, "generations": 10})
    assert response_high.status_code == 422
    assert "less than or equal to 150" in response_high.json()["detail"][0]["msg"]

async def test_post_evolution_run_settings_maxSpringRest_less_than_minSpringRest(async_client):
    '''Test invalid request body: maxSpringRest less than minSpringRest.'''
    invalid_settings = VALID_SETTINGS.copy()
    invalid_settings["minSpringRest"] = 100
    invalid_settings["maxSpringRest"] = 90
    request_body = {
        "settings": invalid_settings,
        "generations": 10
    }
    response = await async_client.post("/api/evolution/run", json=request_body)
    assert response.status_code == 422
    assert "detail" in response.json()
    assert "minSpringRest must be less than or equal to maxSpringRest" in response.json()["detail"][0]["msg"]

async def test_post_evolution_run_settings_minInitialSpringLength_out_of_range(async_client):
    '''Test invalid request body: minInitialSpringLength too low or high.'''
    # Too low
    invalid_settings_low = VALID_SETTINGS.copy()
    invalid_settings_low["minInitialSpringLength"] = 29.9
    response_low = await async_client.post("/api/evolution/run", json={"settings": invalid_settings_low, "generations": 10})
    assert response_low.status_code == 422
    assert "greater than or equal to 30" in response_low.json()["detail"][0]["msg"]

    # Too high
    invalid_settings_high = VALID_SETTINGS.copy()
    invalid_settings_high["minInitialSpringLength"] = 70.1
    response_high = await async_client.post("/api/evolution/run", json={"settings": invalid_settings_high, "generations": 10})
    assert response_high.status_code == 422
    assert "less than or equal to 70" in response_high.json()["detail"][0]["msg"]

async def test_post_evolution_run_settings_maxInitialSpringLength_out_of_range(async_client):
    '''Test invalid request body: maxInitialSpringLength too low or high.'''
    # Too low
    invalid_settings_low = VALID_SETTINGS.copy()
    invalid_settings_low["maxInitialSpringLength"] = 29.9
    response_low = await async_client.post("/api/evolution/run", json={"settings": invalid_settings_low, "generations": 10})
    assert response_low.status_code == 422
    assert "greater than or equal to 30" in response_low.json()["detail"][0]["msg"]

    # Too high
    invalid_settings_high = VALID_SETTINGS.copy()
    invalid_settings_high["maxInitialSpringLength"] = 70.1
    response_high = await async_client.post("/api/evolution/run", json={"settings": invalid_settings_high, "generations": 10})
    assert response_high.status_code == 422
    assert "less than or equal to 70" in response_high.json()["detail"][0]["msg"]

async def test_post_evolution_run_settings_maxInitialSpringLength_less_than_minInitialSpringLength(async_client):
    '''Test invalid request body: maxInitialSpringLength less than minInitialSpringLength.'''
    invalid_settings = VALID_SETTINGS.copy()
    invalid_settings["minInitialSpringLength"] = 60
    invalid_settings["maxInitialSpringLength"] = 50
    request_body = {
        "settings": invalid_settings,
        "generations": 10
    }
    response = await async_client.post("/api/evolution/run", json=request_body)
    assert response.status_code == 422
    assert "detail" in response.json()
    assert "minInitialSpringLength must be less than or equal to maxInitialSpringLength" in response.json()["detail"][0]["msg"]

async def test_post_evolution_run_settings_groundFriction_invalid_type(async_client):
    '''Test invalid request body: groundFriction with wrong type.'''
    invalid_settings = VALID_SETTINGS.copy()
    invalid_settings["groundFriction"] = "not_a_float"
    request_body = {
        "settings": invalid_settings,
        "generations": 10
    }
    response = await async_client.post("/api/evolution/run", json=request_body)
    assert response.status_code == 422
    assert "valid number" in response.json()["detail"][0]["msg"]

async def test_post_evolution_run_settings_groundFriction_negative(async_client):
    '''Test invalid request body: groundFriction is negative.'''
    invalid_settings = VALID_SETTINGS.copy()
    invalid_settings["groundFriction"] = -0.1
    request_body = {
        "settings": invalid_settings,
        "generations": 10
    }
    response = await async_client.post("/api/evolution/run", json=request_body)
    assert response.status_code == 422
    assert "greater than or equal to 0" in response.json()["detail"][0]["msg"]

async def test_post_evolution_run_settings_groundFriction_too_high(async_client):
    '''Test invalid request body: groundFriction is greater than 1.0.'''
    invalid_settings = VALID_SETTINGS.copy()
    invalid_settings["groundFriction"] = 1.1
    request_body = {
        "settings": invalid_settings,
        "generations": 10
    }
    response = await async_client.post("/api/evolution/run", json=request_body)
    assert response.status_code == 422
    assert "less than or equal to 1" in response.json()["detail"][0]["msg"]

async def test_post_evolution_run_settings_jointWeight_invalid_type(async_client):
    '''Test invalid request body: jointWeight with wrong type.'''
    invalid_settings = VALID_SETTINGS.copy()
    invalid_settings["jointWeight"] = "not_a_float"
    request_body = {
        "settings": invalid_settings,
        "generations": 10
    }
    response = await async_client.post("/api/evolution/run", json=request_body)
    assert response.status_code == 422
    assert "valid number" in response.json()["detail"][0]["msg"]

async def test_post_evolution_run_settings_jointWeight_negative_or_zero(async_client):
    '''Test invalid request body: jointWeight is negative or zero.'''
    # Zero
    invalid_settings_zero = VALID_SETTINGS.copy()
    invalid_settings_zero["jointWeight"] = 0.0
    response_zero = await async_client.post("/api/evolution/run", json={"settings": invalid_settings_zero, "generations": 10})
    assert response_zero.status_code == 422
    assert "greater than 0" in response_zero.json()["detail"][0]["msg"]

    # Negative
    invalid_settings_negative = VALID_SETTINGS.copy()
    invalid_settings_negative["jointWeight"] = -1.0
    response_negative = await async_client.post("/api/evolution/run", json={"settings": invalid_settings_negative, "generations": 10})
    assert response_negative.status_code == 422
    assert "greater than 0" in response_negative.json()["detail"][0]["msg"]

async def test_post_evolution_run_settings_minJoints_out_of_range(async_client):
    '''Test invalid request body: minJoints too low or high.'''
    # Too low
    invalid_settings_low = VALID_SETTINGS.copy()
    invalid_settings_low["minJoints"] = 2
    response_low = await async_client.post("/api/evolution/run", json={"settings": invalid_settings_low, "generations": 10})
    assert response_low.status_code == 422
    assert "greater than or equal to 3" in response_low.json()["detail"][0]["msg"]

    # Too high
    invalid_settings_high = VALID_SETTINGS.copy()
    invalid_settings_high["minJoints"] = 9
    response_high = await async_client.post("/api/evolution/run", json={"settings": invalid_settings_high, "generations": 10})
    assert response_high.status_code == 422
    assert "less than or equal to 8" in response_high.json()["detail"][0]["msg"]

async def test_post_evolution_run_settings_minJoints_invalid_type(async_client):
    '''Test invalid request body: minJoints with wrong type.'''
    invalid_settings = VALID_SETTINGS.copy()
    invalid_settings["minJoints"] = 3.5
    request_body = {
        "settings": invalid_settings,
        "generations": 10
    }
    response = await async_client.post("/api/evolution/run", json=request_body)
    assert response.status_code == 422
    assert "valid integer" in response.json()["detail"][0]["msg"]

async def test_post_evolution_run_settings_maxJoints_out_of_range(async_client):
    '''Test invalid request body: maxJoints too low or high.'''
    # Too low
    invalid_settings_low = VALID_SETTINGS.copy()
    invalid_settings_low["maxJoints"] = 2
    response_low = await async_client.post("/api/evolution/run", json={"settings": invalid_settings_low, "generations": 10})
    assert response_low.status_code == 422
    assert "greater than or equal to 3" in response_low.json()["detail"][0]["msg"]

    # Too high
    invalid_settings_high = VALID_SETTINGS.copy()
    invalid_settings_high["maxJoints"] = 9
    response_high = await async_client.post("/api/evolution/run", json={"settings": invalid_settings_high, "generations": 10})
    assert response_high.status_code == 422
    assert "less than or equal to 8" in response_high.json()["detail"][0]["msg"]

async def test_post_evolution_run_settings_maxJoints_invalid_type(async_client):
    '''Test invalid request body: maxJoints with wrong type.'''
    invalid_settings = VALID_SETTINGS.copy()
    invalid_settings["maxJoints"] = 8.5
    request_body = {
        "settings": invalid_settings,
        "generations": 10
    }
    response = await async_client.post("/api/evolution/run", json=request_body)
    assert response.status_code == 422
    assert "valid integer" in response.json()["detail"][0]["msg"]

async def test_post_evolution_run_settings_maxJoints_less_than_minJoints(async_client):
    '''Test invalid request body: maxJoints less than minJoints.'''
    invalid_settings = VALID_SETTINGS.copy()
    invalid_settings["minJoints"] = 6
    invalid_settings["maxJoints"] = 5
    request_body = {
        "settings": invalid_settings,
        "generations": 10
    }
    response = await async_client.post("/api/evolution/run", json=request_body)
    assert response.status_code == 422
    assert "detail" in response.json()
    assert "minJoints must be less than or equal to maxJoints" in response.json()["detail"][0]["msg"]

async def test_post_evolution_run_settings_springStiffness_invalid_type(async_client):
    '''Test invalid request body: springStiffness with wrong type.'''
    invalid_settings = VALID_SETTINGS.copy()
    invalid_settings["springStiffness"] = "not_a_float"
    request_body = {
        "settings": invalid_settings,
        "generations": 10
    }
    response = await async_client.post("/api/evolution/run", json=request_body)
    assert response.status_code == 422
    assert "valid number" in response.json()["detail"][0]["msg"]

async def test_post_evolution_run_settings_springStiffness_negative_or_zero(async_client):
    '''Test invalid request body: springStiffness is negative or zero.'''
    # Zero
    invalid_settings_zero = VALID_SETTINGS.copy()
    invalid_settings_zero["springStiffness"] = 0.0
    response_zero = await async_client.post("/api/evolution/run", json={"settings": invalid_settings_zero, "generations": 10})
    assert response_zero.status_code == 422
    assert "greater than 0" in response_zero.json()["detail"][0]["msg"]

    # Negative
    invalid_settings_negative = VALID_SETTINGS.copy()
    invalid_settings_negative["springStiffness"] = -1.0
    response_negative = await async_client.post("/api/evolution/run", json={"settings": invalid_settings_negative, "generations": 10})
    assert response_negative.status_code == 422
    assert "greater than 0" in response_negative.json()["detail"][0]["msg"]

async def test_post_evolution_run_settings_nnWeightMutationChance_out_of_range(async_client):
    '''Test invalid request body: nnWeightMutationChance out of 0-100 range.'''
    # Too low
    invalid_settings_low = VALID_SETTINGS.copy()
    invalid_settings_low["nnWeightMutationChance"] = -1
    response_low = await async_client.post("/api/evolution/run", json={"settings": invalid_settings_low, "generations": 10})
    assert response_low.status_code == 422
    assert "greater than or equal to 0" in response_low.json()["detail"][0]["msg"]

    # Too high
    invalid_settings_high = VALID_SETTINGS.copy()
    invalid_settings_high["nnWeightMutationChance"] = 101
    response_high = await async_client.post("/api/evolution/run", json={"settings": invalid_settings_high, "generations": 10})
    assert response_high.status_code == 422
    assert "less than or equal to 100" in response_high.json()["detail"][0]["msg"]

async def test_post_evolution_run_settings_nnWeightMutationChance_invalid_type(async_client):
    '''Test invalid request body: nnWeightMutationChance with wrong type.'''
    invalid_settings = VALID_SETTINGS.copy()
    invalid_settings["nnWeightMutationChance"] = "not_an_int"
    request_body = {
        "settings": invalid_settings,
        "generations": 10
    }
    response = await async_client.post("/api/evolution/run", json=request_body)
    assert response.status_code == 422
    assert "valid integer" in response.json()["detail"][0]["msg"]

async def test_post_evolution_run_settings_jointPositionMutationChance_out_of_range(async_client):
    '''Test invalid request body: jointPositionMutationChance out of 0-100 range.'''
    # Too low
    invalid_settings_low = VALID_SETTINGS.copy()
    invalid_settings_low["jointPositionMutationChance"] = -1
    response_low = await async_client.post("/api/evolution/run", json={"settings": invalid_settings_low, "generations": 10})
    assert response_low.status_code == 422
    assert "greater than or equal to 0" in response_low.json()["detail"][0]["msg"]

    # Too high
    invalid_settings_high = VALID_SETTINGS.copy()
    invalid_settings_high["jointPositionMutationChance"] = 101
    response_high = await async_client.post("/api/evolution/run", json={"settings": invalid_settings_high, "generations": 10})
    assert response_high.status_code == 422
    assert "less than or equal to 100" in response_high.json()["detail"][0]["msg"]

async def test_post_evolution_run_settings_jointPositionMutationChance_invalid_type(async_client):
    '''Test invalid request body: jointPositionMutationChance with wrong type.'''
    invalid_settings = VALID_SETTINGS.copy()
    invalid_settings["jointPositionMutationChance"] = "not_an_int"
    request_body = {
        "settings": invalid_settings,
        "generations": 10
    }
    response = await async_client.post("/api/evolution/run", json=request_body)
    assert response.status_code == 422
    assert "valid integer" in response.json()["detail"][0]["msg"]

async def test_post_evolution_run_settings_addRemoveJointMutationChance_out_of_range(async_client):
    '''Test invalid request body: addRemoveJointMutationChance out of 0-100 range.'''
    # Too low
    invalid_settings_low = VALID_SETTINGS.copy()
    invalid_settings_low["addRemoveJointMutationChance"] = -1
    response_low = await async_client.post("/api/evolution/run", json={"settings": invalid_settings_low, "generations": 10})
    assert response_low.status_code == 422
    assert "greater than or equal to 0" in response_low.json()["detail"][0]["msg"]

    # Too high
    invalid_settings_high = VALID_SETTINGS.copy()
    invalid_settings_high["addRemoveJointMutationChance"] = 101
    response_high = await async_client.post("/api/evolution/run", json={"settings": invalid_settings_high, "generations": 10})
    assert response_high.status_code == 422
    assert "less than or equal to 100" in response_high.json()["detail"][0]["msg"]

async def test_post_evolution_run_settings_addRemoveJointMutationChance_invalid_type(async_client):
    '''Test invalid request body: addRemoveJointMutationChance with wrong type.'''
    invalid_settings = VALID_SETTINGS.copy()
    invalid_settings["addRemoveJointMutationChance"] = "not_an_int"
    request_body = {
        "settings": invalid_settings,
        "generations": 10
    }
    response = await async_client.post("/api/evolution/run", json=request_body)
    assert response.status_code == 422
    assert "valid integer" in response.json()["detail"][0]["msg"]

async def test_post_evolution_run_settings_addRemoveMuscleMutationChance_out_of_range(async_client):
    '''Test invalid request body: addRemoveMuscleMutationChance out of 0-100 range.'''
    # Too low
    invalid_settings_low = VALID_SETTINGS.copy()
    invalid_settings_low["addRemoveMuscleMutationChance"] = -1
    response_low = await async_client.post("/api/evolution/run", json={"settings": invalid_settings_low, "generations": 10})
    assert response_low.status_code == 422
    assert "greater than or equal to 0" in response_low.json()["detail"][0]["msg"]

    # Too high
    invalid_settings_high = VALID_SETTINGS.copy()
    invalid_settings_high["addRemoveMuscleMutationChance"] = 101
    response_high = await async_client.post("/api/evolution/run", json={"settings": invalid_settings_high, "generations": 10})
    assert response_high.status_code == 422
    assert "less than or equal to 100" in response_high.json()["detail"][0]["msg"]

async def test_post_evolution_run_settings_addRemoveMuscleMutationChance_invalid_type(async_client):
    '''Test invalid request body: addRemoveMuscleMutationChance with wrong type.'''
    invalid_settings = VALID_SETTINGS.copy()
    invalid_settings["addRemoveMuscleMutationChance"] = "not_an_int"
    request_body = {
        "settings": invalid_settings,
        "generations": 10
    }
    response = await async_client.post("/api/evolution/run", json=request_body)
    assert response.status_code == 422
    assert "valid integer" in response.json()["detail"][0]["msg"]

async def test_post_evolution_run_settings_missing_minSpringRest(async_client):
    '''Test invalid request body: missing minSpringRest field in settings.'''
    invalid_settings = VALID_SETTINGS.copy()
    del invalid_settings["minSpringRest"]
    request_body = {"settings": invalid_settings, "generations": 10}
    response = await async_client.post("/api/evolution/run", json=request_body)
    assert response.status_code == 422
    assert "Field required" in response.json()["detail"][0]["msg"]
    assert "minSpringRest" in response.json()["detail"][0]["loc"][-1]

async def test_post_evolution_run_settings_missing_maxSpringRest(async_client):
    '''Test invalid request body: missing maxSpringRest field in settings.'''
    invalid_settings = VALID_SETTINGS.copy()
    del invalid_settings["maxSpringRest"]
    request_body = {"settings": invalid_settings, "generations": 10}
    response = await async_client.post("/api/evolution/run", json=request_body)
    assert response.status_code == 422
    assert "Field required" in response.json()["detail"][0]["msg"]
    assert "maxSpringRest" in response.json()["detail"][0]["loc"][-1]

async def test_post_evolution_run_settings_missing_minInitialSpringLength(async_client):
    '''Test invalid request body: missing minInitialSpringLength field in settings.'''
    invalid_settings = VALID_SETTINGS.copy()
    del invalid_settings["minInitialSpringLength"]
    request_body = {"settings": invalid_settings, "generations": 10}
    response = await async_client.post("/api/evolution/run", json=request_body)
    assert response.status_code == 422
    assert "Field required" in response.json()["detail"][0]["msg"]
    assert "minInitialSpringLength" in response.json()["detail"][0]["loc"][-1]

async def test_post_evolution_run_settings_missing_maxInitialSpringLength(async_client):
    '''Test invalid request body: missing maxInitialSpringLength field in settings.'''
    invalid_settings = VALID_SETTINGS.copy()
    del invalid_settings["maxInitialSpringLength"]
    request_body = {"settings": invalid_settings, "generations": 10}
    response = await async_client.post("/api/evolution/run", json=request_body)
    assert response.status_code == 422
    assert "Field required" in response.json()["detail"][0]["msg"]
    assert "maxInitialSpringLength" in response.json()["detail"][0]["loc"][-1]

async def test_post_evolution_run_settings_missing_groundFriction(async_client):
    '''Test invalid request body: missing groundFriction field in settings.'''
    invalid_settings = VALID_SETTINGS.copy()
    del invalid_settings["groundFriction"]
    request_body = {"settings": invalid_settings, "generations": 10}
    response = await async_client.post("/api/evolution/run", json=request_body)
    assert response.status_code == 422
    assert "Field required" in response.json()["detail"][0]["msg"]
    assert "groundFriction" in response.json()["detail"][0]["loc"][-1]

async def test_post_evolution_run_settings_missing_jointWeight(async_client):
    '''Test invalid request body: missing jointWeight field in settings.'''
    invalid_settings = VALID_SETTINGS.copy()
    del invalid_settings["jointWeight"]
    request_body = {"settings": invalid_settings, "generations": 10}
    response = await async_client.post("/api/evolution/run", json=request_body)
    assert response.status_code == 422
    assert "Field required" in response.json()["detail"][0]["msg"]
    assert "jointWeight" in response.json()["detail"][0]["loc"][-1]

async def test_post_evolution_run_settings_missing_minJoints(async_client):
    '''Test invalid request body: missing minJoints field in settings.'''
    invalid_settings = VALID_SETTINGS.copy()
    del invalid_settings["minJoints"]
    request_body = {"settings": invalid_settings, "generations": 10}
    response = await async_client.post("/api/evolution/run", json=request_body)
    assert response.status_code == 422
    assert "Field required" in response.json()["detail"][0]["msg"]
    assert "minJoints" in response.json()["detail"][0]["loc"][-1]

async def test_post_evolution_run_settings_missing_maxJoints(async_client):
    '''Test invalid request body: missing maxJoints field in settings.'''
    invalid_settings = VALID_SETTINGS.copy()
    del invalid_settings["maxJoints"]
    request_body = {"settings": invalid_settings, "generations": 10}
    response = await async_client.post("/api/evolution/run", json=request_body)
    assert response.status_code == 422
    assert "Field required" in response.json()["detail"][0]["msg"]
    assert "maxJoints" in response.json()["detail"][0]["loc"][-1]

async def test_post_evolution_run_settings_missing_springStiffness(async_client):
    '''Test invalid request body: missing springStiffness field in settings.'''
    invalid_settings = VALID_SETTINGS.copy()
    del invalid_settings["springStiffness"]
    request_body = {"settings": invalid_settings, "generations": 10}
    response = await async_client.post("/api/evolution/run", json=request_body)
    assert response.status_code == 422
    assert "Field required" in response.json()["detail"][0]["msg"]
    assert "springStiffness" in response.json()["detail"][0]["loc"][-1]

async def test_post_evolution_run_settings_missing_nnWeightMutationChance(async_client):
    '''Test invalid request body: missing nnWeightMutationChance field in settings.'''
    invalid_settings = VALID_SETTINGS.copy()
    del invalid_settings["nnWeightMutationChance"]
    request_body = {"settings": invalid_settings, "generations": 10}
    response = await async_client.post("/api/evolution/run", json=request_body)
    assert response.status_code == 422
    assert "Field required" in response.json()["detail"][0]["msg"]
    assert "nnWeightMutationChance" in response.json()["detail"][0]["loc"][-1]

async def test_post_evolution_run_settings_missing_jointPositionMutationChance(async_client):
    '''Test invalid request body: missing jointPositionMutationChance field in settings.'''
    invalid_settings = VALID_SETTINGS.copy()
    del invalid_settings["jointPositionMutationChance"]
    request_body = {"settings": invalid_settings, "generations": 10}
    response = await async_client.post("/api/evolution/run", json=request_body)
    assert response.status_code == 422
    assert "Field required" in response.json()["detail"][0]["msg"]
    assert "jointPositionMutationChance" in response.json()["detail"][0]["loc"][-1]

async def test_post_evolution_run_settings_missing_addRemoveJointMutationChance(async_client):
    '''Test invalid request body: missing addRemoveJointMutationChance field in settings.'''
    invalid_settings = VALID_SETTINGS.copy()
    del invalid_settings["addRemoveJointMutationChance"]
    request_body = {"settings": invalid_settings, "generations": 10}
    response = await async_client.post("/api/evolution/run", json=request_body)
    assert response.status_code == 422
    assert "Field required" in response.json()["detail"][0]["msg"]
    assert "addRemoveJointMutationChance" in response.json()["detail"][0]["loc"][-1]

async def test_post_evolution_run_settings_missing_addRemoveMuscleMutationChance(async_client):
    '''Test invalid request body: missing addRemoveMuscleMutationChance field in settings.'''
    invalid_settings = VALID_SETTINGS.copy()
    del invalid_settings["addRemoveMuscleMutationChance"]
    request_body = {"settings": invalid_settings, "generations": 10}
    response = await async_client.post("/api/evolution/run", json=request_body)
    assert response.status_code == 422
    assert "Field required" in response.json()["detail"][0]["msg"]
    assert "addRemoveMuscleMutationChance" in response.json()["detail"][0]["loc"][-1]

async def test_post_evolution_run_invalid_settings_not_object(async_client):
    '''Test invalid request body: settings is not a dictionary.'''
    request_body = {
        "settings": "not_an_object", # Invalid type
        "generations": 10
    }
    response = await async_client.post("/api/evolution/run", json=request_body)
    assert response.status_code == 422
    assert "detail" in response.json()
    assert "Input should be a valid dictionary" in response.json()["detail"][0]["msg"]

async def test_post_evolution_run_invalid_settings_null(async_client):
    '''Test invalid request body: settings is null.'''
    request_body = {
        "settings": None, # Invalid type
        "generations": 10
    }
    response = await async_client.post("/api/evolution/run", json=request_body)
    assert response.status_code == 422
    assert "detail" in response.json()
    assert "Input should be a valid dictionary" in response.json()["detail"][0]["msg"]

async def test_post_evolution_run_extra_top_level_field(async_client):
    '''Test invalid request body: extra top-level field.'''
    request_body = {
        "settings": VALID_SETTINGS,
        "generations": 10,
        "extraTopLevelField": "some_value" # Extra field
    }
    response = await async_client.post("/api/evolution/run", json=request_body)
    assert response.status_code == 422
    assert "detail" in response.json()
    assert "Extra inputs are not permitted" in response.json()["detail"][0]["msg"]
    assert "extraTopLevelField" in response.json()["detail"][0]["loc"][-1]

async def test_post_evolution_run_empty_request_body(async_client):
    '''Test invalid request body: empty request body.'''
    request_body = {}
    response = await async_client.post("/api/evolution/run", json=request_body)
    assert response.status_code == 422
    assert "detail" in response.json()
    assert "Field required" in response.json()["detail"][0]["msg"] # Should complain about missing 'settings'
    assert "Field required" in response.json()["detail"][1]["msg"] # Should complain about missing 'generations'

async def test_post_evolution_run_empty_settings_object(async_client):
    '''Test invalid request body: empty settings object.'''
    request_body = {
        "settings": {},
        "generations": 10
    }
    response = await async_client.post("/api/evolution/run", json=request_body)
    assert response.status_code == 422
    assert "detail" in response.json()
    # It should list all missing fields within settings
    assert len(response.json()["detail"]) == len(VALID_SETTINGS) - 1 # All 13 fields required (orchestratorTestMode is optional)
    assert "Field required" in response.json()["detail"][0]["msg"]
    assert "minSpringRest" in response.json()["detail"][0]["loc"][-1] # Check first one as example

# Partition: Valid Settings Boundary Values and Edge Cases (7 tests)
async def test_post_evolution_run_settings_groundFriction_boundary_values(async_client):
    '''Test valid request body: groundFriction at 0.0 and 1.0.'''
    # 0.0
    valid_settings_zero = VALID_SETTINGS.copy()
    valid_settings_zero["groundFriction"] = 0.0
    response_zero = await async_client.post("/api/evolution/run", json={"settings": valid_settings_zero, "generations": 10})
    assert response_zero.status_code == 202

    # 1.0
    valid_settings_one = VALID_SETTINGS.copy()
    valid_settings_one["groundFriction"] = 1.0
    response_one = await async_client.post("/api/evolution/run", json={"settings": valid_settings_one, "generations": 10})
    assert response_one.status_code == 202

async def test_post_evolution_run_settings_jointWeight_small_positive(async_client):
    '''Test valid request body: jointWeight at a very small positive value.'''
    valid_settings = VALID_SETTINGS.copy()
    valid_settings["jointWeight"] = 0.0001
    response = await async_client.post("/api/evolution/run", json={"settings": valid_settings, "generations": 10})
    assert response.status_code == 202

async def test_post_evolution_run_settings_springStiffness_small_positive(async_client):
    '''Test valid request body: springStiffness at a very small positive value.'''
    valid_settings = VALID_SETTINGS.copy()
    valid_settings["springStiffness"] = 0.0001
    response = await async_client.post("/api/evolution/run", json={"settings": valid_settings, "generations": 10})
    assert response.status_code == 202

async def test_post_evolution_run_settings_minMaxSpringRest_equal_and_valid(async_client):
    '''Test valid request body: minSpringRest equals maxSpringRest and valid.'''
    valid_settings = VALID_SETTINGS.copy()
    valid_settings["minSpringRest"] = 100
    valid_settings["maxSpringRest"] = 100
    response = await async_client.post("/api/evolution/run", json={"settings": valid_settings, "generations": 10})
    assert response.status_code == 202

async def test_post_evolution_run_settings_minMaxInitialSpringLength_equal_and_valid(async_client):
    '''Test valid request body: minInitialSpringLength equals maxInitialSpringLength and valid.'''
    valid_settings = VALID_SETTINGS.copy()
    valid_settings["minInitialSpringLength"] = 50
    valid_settings["maxInitialSpringLength"] = 50
    response = await async_client.post("/api/evolution/run", json={"settings": valid_settings, "generations": 10})
    assert response.status_code == 202

async def test_post_evolution_run_settings_minMaxJoints_equal_and_valid(async_client):
    '''Test valid request body: minJoints equals maxJoints and valid.'''
    valid_settings = VALID_SETTINGS.copy()
    valid_settings["minJoints"] = 5
    valid_settings["maxJoints"] = 5
    response = await async_client.post("/api/evolution/run", json={"settings": valid_settings, "generations": 10})
    assert response.status_code == 202

async def test_post_evolution_run_settings_mutation_chances_boundary_values(async_client):
    '''Test valid request body: mutation chances at 0 and 100.'''
    mutation_chance_fields = [
        "nnWeightMutationChance",
        "jointPositionMutationChance",
        "addRemoveJointMutationChance",
        "addRemoveMuscleMutationChance"
    ]

    for field in mutation_chance_fields:
        # Test 0
        valid_settings_zero = VALID_SETTINGS.copy()
        valid_settings_zero[field] = 0
        response_zero = await async_client.post("/api/evolution/run", json={"settings": valid_settings_zero, "generations": 10})
        assert response_zero.status_code == 202, f"Failed for {field}=0"

        # Test 100
        valid_settings_hundred = VALID_SETTINGS.copy()
        valid_settings_hundred[field] = 100
        response_hundred = await async_client.post("/api/evolution/run", json={"settings": valid_settings_hundred, "generations": 10})
        assert response_hundred.status_code == 202, f"Failed for {field}=100"

# Partition: Simulation Failure (1 test)
async def test_post_evolution_run_simulation_failure(async_client):
    '''
    Test POST /api/evolution/run when src.orchestrator.orchestrator.run_simulation
    raises an exception, leading to a 500 error for subsequent GET /results.
    '''
    request_body = {
        "settings": VALID_SETTINGS,
        "generations": 10
    }

    with patch("src.api.endpoints.run_simulation", side_effect=Exception("Orchestrator test failure")):
        with patch("src.api.endpoints._run_simulation_and_store_results", new_callable=AsyncMock) as mock_store_results:
            completion_future = asyncio.Future()
            mock_store_results.return_value = completion_future

            response = await async_client.post("/api/evolution/run", json=request_body)

            assert response.status_code == 202
            response_data = response.json()
            assert "runId" in response_data
            run_id = response_data["runId"]

            assert _simulation_results_cache.get(run_id) == {"status": "in_progress"}

            try:
                # Call the actual background task function directly to simulate its execution
                await _run_simulation_and_store_results(run_id, VALID_SETTINGS, 10)
            except Exception:
                pass # Expected to raise, then caught and handled by _run_simulation_and_store_results internally

            # After the background task (simulated) attempts to run and fails,
            # the cache should reflect the 'failed' status
            assert _simulation_results_cache.get(run_id)["status"] == "failed"
            assert "error" in _simulation_results_cache.get(run_id)
            assert "Orchestrator test failure" in _simulation_results_cache.get(run_id)["error"]

            # Now, query the /results endpoint for this runId
            results_response = await async_client.get(f"/api/evolution/results/{run_id}")
            assert results_response.status_code == 500
            assert results_response.json()["detail"] == "Simulation failed: Orchestrator test failure"


# --- GET /api/evolution/results/{runId} Tests ---

# Partition: Successful Retrieval and Sorting (11 tests)
async def test_get_evolution_results_success_and_sorting(async_client):
    '''
    Test successful retrieval of results for a given runId.
    Verify response schema and critical sorting.
    Generate mock data that is initially unsorted to confirm the sorting.
    '''
    test_run_id = str(uuid.uuid4())

    mock_fitness_scores = [10.0, 5.0, 15.0] # Unsorted
    mock_playback_data = [[[1,1]], [[2,2]], [[3,3]]] # Corresponds to 10, 5, 15
    mock_initial_positions = [[10,10], [20,20], [30,30]]
    mock_muscle_connectivity = [[[0,1]], [[0,2]], [[1,2]]]

    _simulation_results_cache[test_run_id] = {
        "playbackData": mock_playback_data,
        "fitnessScores": mock_fitness_scores,
        "initialPositions": mock_initial_positions,
        "muscleConnectivity": mock_muscle_connectivity
    }

    response = await async_client.get(f"/api/evolution/results/{test_run_id}")

    assert response.status_code == 200
    response_data = response.json()

    assert "playbackData" in response_data
    assert "fitnessScores" in response_data
    assert "initialPositions" in response_data
    assert "muscleConnectivity" in response_data

    num_creatures = len(mock_fitness_scores)
    assert len(response_data["playbackData"]) == num_creatures
    assert len(response_data["fitnessScores"]) == num_creatures
    assert len(response_data["initialPositions"]) == num_creatures
    assert len(response_data["muscleConnectivity"]) == num_creatures

    expected_sorted_fitness = sorted(mock_fitness_scores, reverse=True)
    assert response_data["fitnessScores"] == expected_sorted_fitness

    expected_sorted_playback_data = [mock_playback_data[2], mock_playback_data[0], mock_playback_data[1]]
    expected_sorted_initial_positions = [mock_initial_positions[2], mock_initial_positions[0], mock_initial_positions[1]]
    expected_sorted_muscle_connectivity = [mock_muscle_connectivity[2], mock_muscle_connectivity[0], mock_muscle_connectivity[1]]

    assert response_data["playbackData"] == expected_sorted_playback_data
    assert response_data["initialPositions"] == expected_sorted_initial_positions
    assert response_data["muscleConnectivity"] == expected_sorted_muscle_connectivity

async def test_get_evolution_results_successful_response_schema_validation(async_client):
    '''
    Test successful retrieval of results and detailed validation of response schema types and structure.
    '''
    test_run_id = str(uuid.uuid4())
    mock_orchestrator_results = {
        "playbackData": [[[1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0]]], # Creature 1, Frame 1, Frame 2
        "fitnessScores": [10.5],
        "initialPositions": [[10.0, 20.0, 30.0, 40.0]],
        "muscleConnectivity": [[[0, 1], [1, 2]]]
    }
    _simulation_results_cache[test_run_id] = mock_orchestrator_results

    response = await async_client.get(f"/api/evolution/results/{test_run_id}")
    assert response.status_code == 200
    response_data = response.json()

    # Verify top-level types
    assert isinstance(response_data["playbackData"], list)
    assert isinstance(response_data["fitnessScores"], list)
    assert isinstance(response_data["initialPositions"], list)
    assert isinstance(response_data["muscleConnectivity"], list)

    # Verify content types and structure for one creature (assuming at least one)
    assert len(response_data["playbackData"]) > 0
    assert isinstance(response_data["playbackData"][0], list) # list of frames
    assert len(response_data["playbackData"][0]) > 0
    assert isinstance(response_data["playbackData"][0][0], list) # list of joint positions
    assert len(response_data["playbackData"][0][0]) > 0
    assert isinstance(response_data["playbackData"][0][0][0], float) # float joint position

    assert len(response_data["fitnessScores"]) > 0
    assert isinstance(response_data["fitnessScores"][0], float)

    assert len(response_data["initialPositions"]) > 0
    assert isinstance(response_data["initialPositions"][0], list) # list of joint positions
    assert len(response_data["initialPositions"][0]) > 0
    assert isinstance(response_data["initialPositions"][0][0], float) # float joint position

    assert len(response_data["muscleConnectivity"]) > 0
    assert isinstance(response_data["muscleConnectivity"][0], list) # list of muscles
    assert len(response_data["muscleConnectivity"][0]) > 0
    assert isinstance(response_data["muscleConnectivity"][0][0], list) # list of two joint indices
    assert len(response_data["muscleConnectivity"][0][0]) == 2
    assert isinstance(response_data["muscleConnectivity"][0][0][0], int) # int joint index


async def test_get_evolution_results_sorting_with_empty_data(async_client):
    '''
    Test sorting behavior when data is empty for a successful run.
    Should return empty lists/arrays for all fields.
    '''
    test_run_id = str(uuid.uuid4())
    _simulation_results_cache[test_run_id] = {
        "playbackData": [],
        "fitnessScores": [],
        "initialPositions": [],
        "muscleConnectivity": []
    }

    response = await async_client.get(f"/api/evolution/results/{test_run_id}")
    assert response.status_code == 200
    response_data = response.json()

    assert response_data["playbackData"] == []
    assert response_data["fitnessScores"] == []
    assert response_data["initialPositions"] == []
    assert response_data["muscleConnectivity"] == []

async def test_get_evolution_results_sorting_with_all_same_fitness_scores(async_client):
    '''
    Test sorting behavior when all fitness scores are identical.
    Should maintain original relative order (stable sort).
    '''
    test_run_id = str(uuid.uuid4())

    mock_fitness_scores = [10.0, 10.0, 10.0]
    mock_playback_data = [[[1,1]], [[2,2]], [[3,3]]] # Distinct data to check order
    mock_initial_positions = [[10,10], [20,20], [30,30]]
    mock_muscle_connectivity = [[[0,1]], [[0,2]], [[1,2]]]

    _simulation_results_cache[test_run_id] = {
        "playbackData": mock_playback_data,
        "fitnessScores": mock_fitness_scores,
        "initialPositions": mock_initial_positions,
        "muscleConnectivity": mock_muscle_connectivity
    }

    response = await async_client.get(f"/api/evolution/results/{test_run_id}")
    assert response.status_code == 200
    response_data = response.json()

    assert response_data["fitnessScores"] == [10.0, 10.0, 10.0]
    assert response_data["playbackData"] == mock_playback_data
    assert response_data["initialPositions"] == mock_initial_positions
    assert response_data["muscleConnectivity"] == mock_muscle_connectivity

async def test_get_evolution_results_sorting_with_duplicate_fitness_scores(async_client):
    '''
    Test sorting behavior with duplicate fitness scores but different associated data.
    Should correctly group duplicates and maintain their relative order (stable sort).
    '''
    test_run_id = str(uuid.uuid4())

    # Unsorted data with duplicates
    mock_fitness_scores = [10.0, 5.0, 15.0, 10.0, 8.0]
    mock_playback_data = [[[1,1]], [[2,2]], [[3,3]], [[4,4]], [[5,5]]]
    mock_initial_positions = [[10,10], [20,20], [30,30], [40,40], [50,50]]
    mock_muscle_connectivity = [[[0,1]], [[0,2]], [[1,2]], [[1,3]], [[2,3]]]

    _simulation_results_cache[test_run_id] = {
        "playbackData": mock_playback_data,
        "fitnessScores": mock_fitness_scores,
        "initialPositions": mock_initial_positions,
        "muscleConnectivity": mock_muscle_connectivity
    }

    response = await async_client.get(f"/api/evolution/results/{test_run_id}")
    assert response.status_code == 200
    response_data = response.json()

    expected_sorted_fitness = [15.0, 10.0, 10.0, 8.0, 5.0]
    expected_sorted_playback_data = [mock_playback_data[2], mock_playback_data[0], mock_playback_data[3], mock_playback_data[4], mock_playback_data[1]]
    expected_sorted_initial_positions = [mock_initial_positions[2], mock_initial_positions[0], mock_initial_positions[3], mock_initial_positions[4], mock_initial_positions[1]]
    expected_sorted_muscle_connectivity = [mock_muscle_connectivity[2], mock_muscle_connectivity[0], mock_muscle_connectivity[3], mock_muscle_connectivity[4], mock_muscle_connectivity[1]]

    assert response_data["fitnessScores"] == expected_sorted_fitness
    assert response_data["playbackData"] == expected_sorted_playback_data
    assert response_data["initialPositions"] == expected_sorted_initial_positions
    assert response_data["muscleConnectivity"] == expected_sorted_muscle_connectivity

async def test_get_evolution_results_sorting_large_number_of_creatures(async_client):
    '''
    Test sorting behavior with a large number of creatures.
    '''
    test_run_id = str(uuid.uuid4())
    num_creatures = 100 # A typical population size

    random.seed(42) # For reproducibility
    mock_fitness_scores = [round(random.uniform(0, 100), 2) for _ in range(num_creatures)]
    mock_playback_data = [[[i, i+1]] for i in range(num_creatures)]
    mock_initial_positions = [[i*10, i*10+1] for i in range(num_creatures)]
    mock_muscle_connectivity = [[[i, (i+1)%num_creatures]] for i in range(num_creatures)]

    _simulation_results_cache[test_run_id] = {
        "playbackData": mock_playback_data,
        "fitnessScores": mock_fitness_scores,
        "initialPositions": mock_initial_positions,
        "muscleConnectivity": mock_muscle_connectivity
    }

    response = await async_client.get(f"/api/evolution/results/{test_run_id}")
    assert response.status_code == 200
    response_data = response.json()

    indexed_data = sorted(
        [(mock_fitness_scores[i], i) for i in range(num_creatures)],
        key=lambda x: x[0],
        reverse=True
    )

    expected_sorted_fitness = [item[0] for item in indexed_data]
    expected_sorted_playback_data = [mock_playback_data[item[1]] for item in indexed_data]
    expected_sorted_initial_positions = [mock_initial_positions[item[1]] for item in indexed_data]
    expected_sorted_muscle_connectivity = [mock_muscle_connectivity[item[1]] for item in indexed_data]

    assert response_data["fitnessScores"] == expected_sorted_fitness
    assert response_data["playbackData"] == expected_sorted_playback_data
    assert response_data["initialPositions"] == expected_sorted_initial_positions
    assert response_data["muscleConnectivity"] == expected_sorted_muscle_connectivity

async def test_get_evolution_results_sorting_with_negative_fitness_scores(async_client):
    '''Test sorting behavior with negative fitness scores.'''
    test_run_id = str(uuid.uuid4())
    mock_fitness_scores = [-10.0, -5.0, -15.0]
    mock_playback_data = [[[1,1]], [[2,2]], [[3,3]]]
    mock_initial_positions = [[10,10], [20,20], [30,30]]
    mock_muscle_connectivity = [[[0,1]], [[0,2]], [[1,2]]]

    _simulation_results_cache[test_run_id] = {
        "playbackData": mock_playback_data,
        "fitnessScores": mock_fitness_scores,
        "initialPositions": mock_initial_positions,
        "muscleConnectivity": mock_muscle_connectivity
    }
    response = await async_client.get(f"/api/evolution/results/{test_run_id}")
    assert response.status_code == 200
    response_data = response.json()
    expected_sorted_fitness = [-5.0, -10.0, -15.0]
    expected_sorted_playback_data = [mock_playback_data[1], mock_playback_data[0], mock_playback_data[2]]
    assert response_data["fitnessScores"] == expected_sorted_fitness
    assert response_data["playbackData"] == expected_sorted_playback_data

async def test_get_evolution_results_sorting_with_zero_fitness_scores(async_client):
    '''Test sorting behavior with zero fitness scores.'''
    test_run_id = str(uuid.uuid4())
    mock_fitness_scores = [0.0, 5.0, 0.0]
    mock_playback_data = [[[1,1]], [[2,2]], [[3,3]]]
    mock_initial_positions = [[10,10], [20,20], [30,30]]
    mock_muscle_connectivity = [[[0,1]], [[0,2]], [[1,2]]]

    _simulation_results_cache[test_run_id] = {
        "playbackData": mock_playback_data,
        "fitnessScores": mock_fitness_scores,
        "initialPositions": mock_initial_positions,
        "muscleConnectivity": mock_muscle_connectivity
    }
    response = await async_client.get(f"/api/evolution/results/{test_run_id}")
    assert response.status_code == 200
    response_data = response.json()
    expected_sorted_fitness = [5.0, 0.0, 0.0]
    expected_sorted_playback_data = [mock_playback_data[1], mock_playback_data[0], mock_playback_data[2]]
    assert response_data["fitnessScores"] == expected_sorted_fitness
    assert response_data["playbackData"] == expected_sorted_playback_data

async def test_get_evolution_results_sorting_with_mixed_fitness_scores(async_client):
    '''Test sorting behavior with mixed positive, negative, and zero fitness scores.'''
    test_run_id = str(uuid.uuid4())
    mock_fitness_scores = [10.0, -5.0, 0.0, 15.0, -1.0]
    mock_playback_data = [[[1]], [[2]], [[3]], [[4]], [[5]]]
    mock_initial_positions = [[10], [20], [30], [40], [50]]
    mock_muscle_connectivity = [[[0]], [[1]], [[2]], [[3]], [[4]]]

    _simulation_results_cache[test_run_id] = {
        "playbackData": mock_playback_data,
        "fitnessScores": mock_fitness_scores,
        "initialPositions": mock_initial_positions,
        "muscleConnectivity": mock_muscle_connectivity
    }
    response = await async_client.get(f"/api/evolution/results/{test_run_id}")
    assert response.status_code == 200
    response_data = response.json()
    expected_sorted_fitness = [15.0, 10.0, 0.0, -1.0, -5.0]
    expected_sorted_playback_data = [mock_playback_data[3], mock_playback_data[0], mock_playback_data[2], mock_playback_data[4], mock_playback_data[1]]
    assert response_data["fitnessScores"] == expected_sorted_fitness
    assert response_data["playbackData"] == expected_sorted_playback_data

async def test_get_evolution_results_sorting_with_float_precision_differences(async_client):
    '''Test sorting behavior with float precision differences.'''
    test_run_id = str(uuid.uuid4())
    mock_fitness_scores = [10.001, 10.000, 9.999]
    mock_playback_data = [[[1]], [[2]], [[3]]]
    mock_initial_positions = [[10], [20], [30]]
    mock_muscle_connectivity = [[[0]], [[1]], [[2]]]

    _simulation_results_cache[test_run_id] = {
        "playbackData": mock_playback_data,
        "fitnessScores": mock_fitness_scores,
        "initialPositions": mock_initial_positions,
        "muscleConnectivity": mock_muscle_connectivity
    }
    response = await async_client.get(f"/api/evolution/results/{test_run_id}")
    assert response.status_code == 200
    response_data = response.json()
    expected_sorted_fitness = [10.001, 10.000, 9.999]
    expected_sorted_playback_data = [mock_playback_data[0], mock_playback_data[1], mock_playback_data[2]]
    assert response_data["fitnessScores"] == expected_sorted_fitness
    assert response_data["playbackData"] == expected_sorted_playback_data

async def test_get_evolution_results_sorting_with_single_creature(async_client):
    '''Test sorting behavior with a single creature.'''
    test_run_id = str(uuid.uuid4())
    mock_fitness_scores = [20.0]
    mock_playback_data = [[[10,20]]]
    mock_initial_positions = [[5,5]]
    mock_muscle_connectivity = [[[0,1]]]

    _simulation_results_cache[test_run_id] = {
        "playbackData": mock_playback_data,
        "fitnessScores": mock_fitness_scores,
        "initialPositions": mock_initial_positions,
        "muscleConnectivity": mock_muscle_connectivity
    }
    response = await async_client.get(f"/api/evolution/results/{test_run_id}")
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["fitnessScores"] == mock_fitness_scores
    assert response_data["playbackData"] == mock_playback_data

async def test_get_evolution_results_sorting_with_two_creatures(async_client):
    '''Test sorting behavior with two creatures.'''
    test_run_id = str(uuid.uuid4())
    mock_fitness_scores = [5.0, 15.0]
    mock_playback_data = [[[1]], [[2]]]
    mock_initial_positions = [[10], [20]]
    mock_muscle_connectivity = [[[0]], [[1]]]

    _simulation_results_cache[test_run_id] = {
        "playbackData": mock_playback_data,
        "fitnessScores": mock_fitness_scores,
        "initialPositions": mock_initial_positions,
        "muscleConnectivity": mock_muscle_connectivity
    }
    response = await async_client.get(f"/api/evolution/results/{test_run_id}")
    assert response.status_code == 200
    response_data = response.json()
    expected_sorted_fitness = [15.0, 5.0]
    expected_sorted_playback_data = [mock_playback_data[1], mock_playback_data[0]]
    assert response_data["fitnessScores"] == expected_sorted_fitness
    assert response_data["playbackData"] == expected_sorted_playback_data


# Partition: Status and Error Handling (5 tests)
async def test_get_evolution_results_not_found(async_client):
    '''Test for non-existent runId (expect 404).'''
    non_existent_run_id = str(uuid.uuid4())
    response = await async_client.get(f"/api/evolution/results/{non_existent_run_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Run ID not found."

async def test_get_evolution_results_invalid_run_id_format(async_client):
    '''Test for invalid runId format (expect 422).'''
    invalid_run_id = "not-a-valid-uuid"
    response = await async_client.get(f"/api/evolution/results/{invalid_run_id}")
    assert response.status_code == 422
    assert "detail" in response.json()
    assert "Input should be a valid UUID, invalid character" in response.json()["detail"][0]["msg"]

async def test_get_evolution_results_empty_run_id_string(async_client):
    '''Test for empty runId string (expect 404).'''
    invalid_run_id = ""
    response = await async_client.get(f"/api/evolution/results/{invalid_run_id}")
    assert response.status_code == 404
    assert response.json()['detail'] == 'Not Found'

async def test_get_evolution_results_in_progress(async_client):
    '''Test for in-progress runId (expect 202).'''
    in_progress_run_id = str(uuid.uuid4())
    _simulation_results_cache[in_progress_run_id] = {"status": "in_progress"}
    response = await async_client.get(f"/api/evolution/results/{in_progress_run_id}")
    assert response.status_code == 202
    assert response.json()["detail"] == "Simulation still in progress."

async def test_get_evolution_results_failed_simulation(async_client):
    '''Test for failed simulation runId (expect 500).'''
    failed_run_id = str(uuid.uuid4())
    _simulation_results_cache[failed_run_id] = {"status": "failed", "error": "Test simulation error"}
    response = await async_client.get(f"/api/evolution/results/{failed_run_id}")
    assert response.status_code == 500
    assert response.json()["detail"] == "Simulation failed: Test simulation error"

# Partition: Incomplete/Malformed Data in Cache (15 tests)
async def test_get_evolution_results_incomplete_data_in_cache_missing_initialPositions(async_client):
    '''Test for incomplete data in cache (missing initialPositions, expect 500).'''
    incomplete_run_id = str(uuid.uuid4())
    _simulation_results_cache[incomplete_run_id] = {
        "playbackData": [[[1,1]]],
        "fitnessScores": [10.0],
        "muscleConnectivity": [[[0,1]]]
    }
    response = await async_client.get(f"/api/evolution/results/{incomplete_run_id}")
    assert response.status_code == 500
    assert response.json()["detail"] == "Incomplete simulation results stored."

async def test_get_evolution_results_incomplete_data_missing_playback_data(async_client):
    '''Test for incomplete data in cache (missing playbackData, expect 500).'''
    incomplete_run_id = str(uuid.uuid4())
    _simulation_results_cache[incomplete_run_id] = {
        "fitnessScores": [10.0],
        "initialPositions": [[1,1]],
        "muscleConnectivity": [[[0,1]]]
    }
    response = await async_client.get(f"/api/evolution/results/{incomplete_run_id}")
    assert response.status_code == 500
    assert response.json()["detail"] == "Incomplete simulation results stored."

async def test_get_evolution_results_incomplete_data_missing_fitness_scores(async_client):
    '''Test for incomplete data in cache (missing fitnessScores, expect 500).'''
    incomplete_run_id = str(uuid.uuid4())
    _simulation_results_cache[incomplete_run_id] = {
        "playbackData": [[[1,1]]],
        "initialPositions": [[1,1]],
        "muscleConnectivity": [[[0,1]]]
    }
    response = await async_client.get(f"/api/evolution/results/{incomplete_run_id}")
    assert response.status_code == 500
    assert response.json()["detail"] == "Incomplete simulation results stored."

async def test_get_evolution_results_incomplete_data_missing_muscle_connectivity(async_client):
    '''Test for incomplete data in cache (missing muscleConnectivity, expect 500).'''
    incomplete_run_id = str(uuid.uuid4())
    _simulation_results_cache[incomplete_run_id] = {
        "playbackData": [[[1,1]]],
        "fitnessScores": [10.0],
        "initialPositions": [[1,1]]
    }
    response = await async_client.get(f"/api/evolution/results/{incomplete_run_id}")
    assert response.status_code == 500
    assert response.json()["detail"] == "Incomplete simulation results stored."

async def test_get_evolution_results_incomplete_data_missing_multiple_keys_1(async_client):
    '''Test for incomplete data in cache (missing playbackData and fitnessScores, expect 500).'''
    incomplete_run_id = str(uuid.uuid4())
    _simulation_results_cache[incomplete_run_id] = {
        "initialPositions": [[1,1]],
        "muscleConnectivity": [[[0,1]]]
    }
    response = await async_client.get(f"/api/evolution/results/{incomplete_run_id}")
    assert response.status_code == 500
    assert response.json()["detail"] == "Incomplete simulation results stored."

async def test_get_evolution_results_incomplete_data_missing_multiple_keys_2(async_client):
    '''Test for incomplete data in cache (missing initialPositions and muscleConnectivity, expect 500).'''
    incomplete_run_id = str(uuid.uuid4())
    _simulation_results_cache[incomplete_run_id] = {
        "playbackData": [[[1,1]]],
        "fitnessScores": [10.0]
    }
    response = await async_client.get(f"/api/evolution/results/{incomplete_run_id}")
    assert response.status_code == 500
    assert response.json()["detail"] == "Incomplete simulation results stored."

async def test_get_evolution_results_incomplete_data_missing_all_but_one_key_playback(async_client):
    '''Test for incomplete data in cache (only playbackData present, expect 500).'''
    incomplete_run_id = str(uuid.uuid4())
    _simulation_results_cache[incomplete_run_id] = {
        "playbackData": [[[1,1]]]
    }
    response = await async_client.get(f"/api/evolution/results/{incomplete_run_id}")
    assert response.status_code == 500
    assert response.json()["detail"] == "Incomplete simulation results stored."

async def test_get_evolution_results_incomplete_data_missing_all_but_one_key_fitness(async_client):
    '''Test for incomplete data in cache (only fitnessScores present, expect 500).'''
    incomplete_run_id = str(uuid.uuid4())
    _simulation_results_cache[incomplete_run_id] = {
        "fitnessScores": [10.0]
    }
    response = await async_client.get(f"/api/evolution/results/{incomplete_run_id}")
    assert response.status_code == 500
    assert response.json()["detail"] == "Incomplete simulation results stored."

async def test_get_evolution_results_data_length_mismatch(async_client):
    '''Test for inconsistent data lengths in cache (expect 500).'''
    test_run_id = str(uuid.uuid4())
    _simulation_results_cache[test_run_id] = {
        "playbackData": [[[1,1]]], # 1 creature
        "fitnessScores": [10.0, 20.0], # 2 creatures
        "initialPositions": [[1,1]],
        "muscleConnectivity": [[[0,1]]]
    }
    response = await async_client.get(f"/api/evolution/results/{test_run_id}")
    assert response.status_code == 500
    assert response.json()["detail"] == "Incomplete simulation results stored."

# These tests will result in a generic 500 "Internal Server Error" from FastAPI due to type errors during processing.
async def test_get_evolution_results_malformed_fitness_scores_non_numeric(async_client):
    '''Test for malformed fitnessScores in cache (non-numeric values, expect 500).'''
    test_run_id = str(uuid.uuid4())
    _simulation_results_cache[test_run_id] = {
        "playbackData": [[[1,1]]],
        "fitnessScores": [10.0, "invalid_score"], # Malformed
        "initialPositions": [[1,1]],
        "muscleConnectivity": [[[0,1]]]
    }
    response = await async_client.get(f"/api/evolution/results/{test_run_id}")
    assert response.status_code == 500
    assert response.json()["detail"] == "Incomplete simulation results stored."

async def test_get_evolution_results_malformed_playback_data_wrong_depth(async_client):
    '''Test for malformed playbackData in cache (wrong nesting/type, expect 500).'''
    test_run_id = str(uuid.uuid4())
    _simulation_results_cache[test_run_id] = {
        "playbackData": [[1,1]], # Should be [[[x,y,...]]] not [[x,y,...]]
        "fitnessScores": [10.0],
        "initialPositions": [[1,1]],
        "muscleConnectivity": [[[0,1]]]
    }
    response = await async_client.get(f"/api/evolution/results/{test_run_id}")
    assert response.status_code == 500
    assert response.json()["detail"] == "Incomplete simulation results stored."

async def test_get_evolution_results_malformed_initial_positions_wrong_depth(async_client):
    '''Test for malformed initialPositions in cache (wrong nesting/type, expect 500).'''
    test_run_id = str(uuid.uuid4())
    _simulation_results_cache[test_run_id] = {
        "playbackData": [[[1,1]]],
        "fitnessScores": [10.0],
        "initialPositions": [1,1], # Should be [[x,y,...]] not [x,y,...]
        "muscleConnectivity": [[[0,1]]]
    }
    response = await async_client.get(f"/api/evolution/results/{test_run_id}")
    assert response.status_code == 500
    assert response.json()["detail"] == "Incomplete simulation results stored."

async def test_get_evolution_results_malformed_muscle_connectivity_wrong_depth(async_client):
    '''Test for malformed muscleConnectivity in cache (wrong nesting/type, expect 500).'''
    test_run_id = str(uuid.uuid4())
    _simulation_results_cache[test_run_id] = {
        "playbackData": [[[1,1]]],
        "fitnessScores": [10.0],
        "initialPositions": [[1,1]],
        "muscleConnectivity": [[0,1]] # Should be [[[idx1, idx2]]] not [[idx1, idx2]]
    }
    response = await async_client.get(f"/api/evolution/results/{test_run_id}")
    assert response.status_code == 500
    assert response.json()["detail"] == "Incomplete simulation results stored."
