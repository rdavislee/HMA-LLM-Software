from fastapi import APIRouter, Depends, HTTPException
from backend.src.models.simulation import SimulationRequest, SimulationResponse
from backend.src.utils.logger import get_logger
from backend.src.services.simulation_manager import ISimulationManager
from backend.src.api.dependencies import get_simulation_manager

logger = get_logger(__name__)
router = APIRouter(prefix="/simulation", tags=["Simulation"])

@router.post("/start", status_code=202, response_model=SimulationResponse)
async def start_simulation(
    sim_request: SimulationRequest,
    manager: ISimulationManager = Depends(get_simulation_manager),
):
    """Starts a new simulation job."""
    logger.info(f"Received simulation start request with settings: {sim_request.settings}")
    job_id = manager.start_simulation(sim_request.settings)
    return SimulationResponse(job_id=job_id, status="running", message="Simulation started.")

@router.get("/{job_id}/status")
async def get_simulation_status(
    job_id: str,
    manager: ISimulationManager = Depends(get_simulation_manager),
):
    """Retrieves the status of a specific simulation job."""
    logger.info(f"Checking status for job {job_id}")
    job = manager.get_job_status(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"job_id": job_id, "status": job.get("status", "unknown")}
