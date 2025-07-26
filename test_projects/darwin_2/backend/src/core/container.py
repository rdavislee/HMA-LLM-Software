from backend.src.services.simulation_manager import SimulationManager, ISimulationManager
from backend.src.utils.logger import get_logger

logger = get_logger(__name__)

class AppState:
    """A container for application state and services."""
    def __init__(self, sim_manager: ISimulationManager):
        self.sim_manager = sim_manager
        self.last_generation_cache = {}
        logger.info("AppState initialized.")

# Instantiate services and the state container as singletons
simulation_manager = SimulationManager()
app_state = AppState(sim_manager=simulation_manager)
