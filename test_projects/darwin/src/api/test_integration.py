import pytest
import httpx
from fastapi.testclient import TestClient
import json
import os
from unittest.mock import patch, Mock # Keep patch and Mock in case they are used elsewhere or for future tests
from src.api.endpoints import ResultsResponse # Keep this import for type hinting/schema knowledge if needed
import time

# Import the FastAPI app instance
# Assuming src.main exposes 'app' as the FastAPI application instance
from src.main import app

def test_full_simulation_workflow():
    '''
    Tests the full simulation workflow:
    1. Sends a POST request to /api/evolution/run to start a simulation.
    2. Polls the /api/evolution/results/{runId} endpoint until the simulation completes.
    3. Asserts that the final result is a 200 OK status, indicating a successful
       simulation completion, and that the data conforms to the schema and sorting.
    '''
    client = TestClient(app)

    # Dummy settings and generations for the POST request
    payload = {
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
            "addRemoveMuscleMutationChance": 5,
            "orchestratorTestMode": True
        },
        "generations": 1
    }

    # 1. Send POST request to start simulation
    post_response = client.post("/api/evolution/run", json=payload)
    assert post_response.status_code == 202
    run_id = post_response.json()["runId"]
    assert run_id is not None

    # 2. Implement polling loop for results
    timeout = 30  # seconds
    poll_interval = 1 # seconds
    start_time = time.time()
    result_response = None
    
    while time.time() - start_time < timeout:
        result_response = client.get(f"/api/evolution/results/{run_id}")
        
        if result_response.status_code == 202:
            # Simulation still in progress, wait and retry
            time.sleep(poll_interval)
        elif result_response.status_code == 200:
            # Simulation completed successfully, perform assertions
            response_data = result_response.json()
            
            # Assert the sorting of fitness scores (descending)
            assert all(response_data["fitnessScores"][i] >= response_data["fitnessScores"][i+1] for i in range(len(response_data["fitnessScores"]) - 1))
            # Assert that all top-level arrays have the same length
            num_creatures = len(response_data["fitnessScores"])
            assert len(response_data["playbackData"]) == num_creatures
            assert len(response_data["initialPositions"]) == num_creatures
            assert len(response_data["muscleConnectivity"]) == num_creatures

            # Assert specific internal structure for the first creature (which should be the fittest)
            if num_creatures > 0:
                first_creature_playback_data_frame_0 = response_data["playbackData"][0][0]
                first_creature_initial_positions = response_data["initialPositions"][0]
                first_creature_muscle_connectivity_0 = response_data["muscleConnectivity"][0][0]

                # Confirm playbackData[0][0] is a List[float] and its length is even.
                assert isinstance(first_creature_playback_data_frame_0, list)
                assert all(isinstance(x, float) for x in first_creature_playback_data_frame_0)
                assert len(first_creature_playback_data_frame_0) % 2 == 0

                # Confirm initialPositions[0] is a List[float] and its length is even.
                assert isinstance(first_creature_initial_positions, list)
                assert all(isinstance(x, float) for x in first_creature_initial_positions)
                assert len(first_creature_initial_positions) % 2 == 0

                # Confirm muscleConnectivity[0][0] is a List[int] of length 2.
                assert isinstance(first_creature_muscle_connectivity_0, list)
                assert all(isinstance(x, int) for x in first_creature_muscle_connectivity_0)
                assert len(first_creature_muscle_connectivity_0) == 2
            
            return # Test passed
        else:
            # Any other unexpected status code (including 500) indicates a failure
            pytest.fail(f"Polling received unexpected status code {result_response.status_code}: {result_response.text}")

    # If the loop finishes, it means a timeout occurred without receiving 200 OK
    pytest.fail(f"Polling timed out after {timeout} seconds without receiving 200 OK. Last status: {result_response.status_code if result_response else 'No response'}")

def test_end_to_end_simulation_flow():
    '''
    Simulates a complete simulation run:
    1. Sends a POST request to /api/evolution/run with a valid payload.
    2. Extracts the runId from the POST response.
    3. Continuously polls GET /api/evolution/results/{runId} until the response
       contains all expected top-level keys.
    4. Asserts that the final successful response conforms to the schema and sorting.
    '''
    client = TestClient(app)

    # Payload as specified in the task
    payload = {
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
            "addRemoveMuscleMutationChance": 5,
            "orchestratorTestMode": True
        },
        "generations": 1 # As per task requirement
    }

    # 1. Send POST request to start simulation
    post_response = client.post("/api/evolution/run", json=payload)
    assert post_response.status_code == 202
    run_id = post_response.json()["runId"]
    assert run_id is not None

    # 2. Implement polling loop for results
    timeout = 60  # seconds, as per task suggestion
    poll_interval = 1 # seconds
    start_time = time.time()
    result_response = None
    
    expected_keys = {"playbackData", "fitnessScores", "initialPositions", "muscleConnectivity"}

    while time.time() - start_time < timeout:
        result_response = client.get(f"/api/evolution/results/{run_id}")
        
        if result_response.status_code == 202:
            # Simulation still in progress, wait and retry
            time.sleep(poll_interval)
        elif result_response.status_code == 200:
            # Simulation completed successfully, perform assertions
            response_data = result_response.json()
            
            # 3. Check for all expected top-level keys
            assert expected_keys.issubset(response_data.keys()), f"Missing keys in response: {expected_keys - response_data.keys()}"

            # 4. Assert schema as per documents/api-guidelines.md
            assert isinstance(response_data["playbackData"], list)
            assert isinstance(response_data["fitnessScores"], list)
            assert isinstance(response_data["initialPositions"], list)
            assert isinstance(response_data["muscleConnectivity"], list)

            # Assert the sorting of fitness scores (descending)
            assert all(response_data["fitnessScores"][i] >= response_data["fitnessScores"][i+1] for i in range(len(response_data["fitnessScores"]) - 1))
            # Assert that all top-level arrays have the same length
            num_creatures = len(response_data["fitnessScores"])
            assert len(response_data["playbackData"]) == num_creatures
            assert len(response_data["initialPositions"]) == num_creatures
            assert len(response_data["muscleConnectivity"]) == num_creatures

            # Assert specific internal structure for the first creature (which should be the fittest)
            if num_creatures > 0:
                first_creature_playback_data_frame_0 = response_data["playbackData"][0][0]
                first_creature_initial_positions = response_data["initialPositions"][0]
                first_creature_muscle_connectivity_0 = response_data["muscleConnectivity"][0][0]

                # Confirm playbackData[0][0] is a List[float] and its length is even.
                assert isinstance(first_creature_playback_data_frame_0, list)
                assert all(isinstance(x, float) for x in first_creature_playback_data_frame_0)
                assert len(first_creature_playback_data_frame_0) % 2 == 0

                # Confirm initialPositions[0] is a List[float] and its length is even.
                assert isinstance(first_creature_initial_positions, list)
                assert all(isinstance(x, float) for x in first_creature_initial_positions)
                assert len(first_creature_initial_positions) % 2 == 0

                # Confirm muscleConnectivity[0][0] is a List[int] of length 2.
                assert isinstance(first_creature_muscle_connectivity_0, list)
                assert all(isinstance(x, int) for x in first_creature_muscle_connectivity_0)
                assert len(first_creature_muscle_connectivity_0) == 2
            
            return # Test passed
        else:
            # Any other unexpected status code (including 500) indicates a failure
            pytest.fail(f"Polling received unexpected status code {result_response.status_code}: {result_response.text}")

    # If the loop finishes, it means a timeout occurred without receiving 200 OK
    pytest.fail(f"Polling timed out after {timeout} seconds without receiving 200 OK. Last status: {result_response.status_code if result_response else 'No response'}")

def test_post_run_endpoint_response_format():
    '''
    Tests that the POST /api/evolution/run endpoint returns a response
    with a 'runId' key and that its value is a string.
    '''
    client = TestClient(app)
    payload = {
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
        "generations": 1
    }
    response = client.post("/api/evolution/run", json=payload)
    assert response.status_code == 202
    response_json = response.json()
    assert isinstance(response_json, dict)
    assert len(response_json) == 1
    assert "runId" in response_json
    assert isinstance(response_json["runId"], str)
    assert len(response_json["runId"]) > 0 # Ensure it's not an empty string

