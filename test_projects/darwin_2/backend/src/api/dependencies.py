from backend.src.core.container import app_state
from backend.src.services.simulation_manager import ISimulationManager

def get_simulation_manager() -> ISimulationManager:
    """Dependency injector for the SimulationManager."""
    return app_state.sim_manager
