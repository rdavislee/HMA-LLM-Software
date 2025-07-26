import uuid
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, BackgroundTasks, HTTPException, status, Path
from pydantic import BaseModel, Field, ConfigDict, model_validator, ValidationError

from src.orchestrator.orchestrator import run_simulation

router = APIRouter()

# In-memory store for simulation results
# Stores Dict[run_id, Dict] where the inner Dict is either the simulation results
# or a status indicator like {"status": "in_progress"} or {"error": "..."}
_simulation_results_cache: Dict[str, Dict[str, Any]] = {}

# Pydantic models for request/response validation

class Settings(BaseModel):
    min_spring_rest: float = Field(..., alias="minSpringRest", ge=50, le=150)
    max_spring_rest: float = Field(..., alias="maxSpringRest", ge=50, le=150)
    min_initial_spring_length: float = Field(..., alias="minInitialSpringLength", ge=30, le=70)
    max_initial_spring_length: float = Field(..., alias="maxInitialSpringLength", ge=30, le=70)
    ground_friction: float = Field(..., alias="groundFriction", ge=0, le=1.0)
    joint_weight: float = Field(..., alias="jointWeight", gt=0)
    min_joints: int = Field(..., alias="minJoints", ge=3, le=8)
    max_joints: int = Field(..., alias="maxJoints", ge=3, le=8)
    spring_stiffness: float = Field(..., alias="springStiffness", gt=0)
    nn_weight_mutation_chance: int = Field(..., alias="nnWeightMutationChance", ge=0, le=100)
    joint_position_mutation_chance: int = Field(..., alias="jointPositionMutationChance", ge=0, le=100)
    add_remove_joint_mutation_chance: int = Field(..., alias="addRemoveJointMutationChance", ge=0, le=100)
    add_remove_muscle_mutation_chance: int = Field(..., alias="addRemoveMuscleMutationChance", ge=0, le=100)
    orchestratorTestMode: Optional[bool] = None

    model_config = ConfigDict(populate_by_name=True, extra='forbid')

    @model_validator(mode='after')
    def check_min_max_values(self):
        if self.min_spring_rest > self.max_spring_rest:
            raise ValueError('minSpringRest must be less than or equal to maxSpringRest')
        if self.min_initial_spring_length > self.max_initial_spring_length:
            raise ValueError('minInitialSpringLength must be less than or equal to maxInitialSpringLength')
        if self.min_joints > self.max_joints:
            raise ValueError('minJoints must be less than or equal to maxJoints')
        return self

class RunRequest(BaseModel):
    settings: Settings
    generations: int = Field(..., gt=0)

    model_config = ConfigDict(extra='forbid')

class RunResponse(BaseModel):
    runId: str

# Models for GET /api/evolution/results/{runId} response
class ResultsResponse(BaseModel):
    playbackData: List[List[List[float]]]
    fitnessScores: List[float]
    initialPositions: List[List[float]]
    muscleConnectivity: List[List[List[int]]]

# Background task function to run simulation and store results
def _run_simulation_and_store_results(run_id: str, settings: Dict, generations: int):
    try:
        results = run_simulation(settings, generations)
        _simulation_results_cache[run_id] = results
    except Exception as e:
        print(f"Error running simulation for runId {run_id}: {e}")
        # Store error state for retrieval, or remove run_id if preferred
        _simulation_results_cache[run_id] = {"status": "failed", "error": str(e)}

@router.post("/evolution/run", response_model=RunResponse, status_code=status.HTTP_202_ACCEPTED)
async def run_evolution(request: RunRequest, background_tasks: BackgroundTasks):
    '''
    Kicks off a new evolution simulation as a background task.
    Returns a unique run ID immediately.
    '''
    run_id = str(uuid.uuid4())
    
    # Store a placeholder to indicate that the simulation is in progress
    _simulation_results_cache[run_id] = {"status": "in_progress"}

    # Convert Pydantic Settings model to a plain dictionary for the orchestrator.
    # The orchestrator and downstream logic expect camelCase keys, so we dump by alias.
    background_tasks.add_task(
        _run_simulation_and_store_results,
        run_id,
        request.settings.model_dump(by_alias=True),
        request.generations
    )
    
    return RunResponse(runId=run_id)

@router.get("/evolution/results/{runId}", response_model=ResultsResponse)
async def get_evolution_results(runId: uuid.UUID = Path(...)):
    '''
    Fetches the results for visualization after a run is complete.
    Results are sorted by fitness scores in descending order.
    '''
    results = _simulation_results_cache.get(str(runId))

    if results is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run ID not found.")
    
    if results.get("status") == "in_progress":
        raise HTTPException(status_code=status.HTTP_202_ACCEPTED, detail="Simulation still in progress.")
    
    if results.get("status") == "failed":
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Simulation failed: {results['error']}")

    # Ensure all required top-level arrays are present and not None.
    # Empty lists are allowed and handled later if all are empty.
    required_keys = ["playbackData", "fitnessScores", "initialPositions", "muscleConnectivity"]
    for key in required_keys:
        if key not in results or results[key] is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Incomplete simulation results stored.")
    
    # Check for consistent lengths of top-level arrays.
    # If all are empty, this check will pass (0 == 0).
    # If some are empty and some are not, it will fail (e.g., 0 != N).
    first_key_len = len(results[required_keys[0]])
    if not all(len(results[key]) == first_key_len for key in required_keys):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Incomplete simulation results stored.")

    # If all lists are empty, return an empty ResultsResponse directly.
    # This handles the "empty data, 200 OK" case.
    if first_key_len == 0:
        return ResultsResponse(
            playbackData=[],
            fitnessScores=[],
            initialPositions=[],
            muscleConnectivity=[]
        )

    try:
        # Parallel sort all top-level arrays by fitnessScores in descending order
        combined = zip(
            results["fitnessScores"],
            results["playbackData"],
            results["initialPositions"],
            results["muscleConnectivity"]
        )
        
        # Sort by fitness (first element of the tuple) in descending order
        sorted_combined = sorted(combined, key=lambda x: x[0], reverse=True)
        
        # Unzip the sorted results
        sorted_fitness_scores, sorted_playback_data, sorted_initial_positions, sorted_muscle_connectivity = zip(*sorted_combined)

        # Convert tuples back to lists for the Pydantic response model
        return ResultsResponse(
            playbackData=list(sorted_playback_data),
            fitnessScores=list(sorted_fitness_scores),
            initialPositions=list(sorted_initial_positions),
            muscleConnectivity=list(sorted_muscle_connectivity)
        )
    except ValidationError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Incomplete simulation results stored.")
    except Exception:
        # Catch any other potential errors during zipping/sorting/unzipping that are not Pydantic ValidationErrors
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
