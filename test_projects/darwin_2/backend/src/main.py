from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.src.api.simulation_router import router as simulation_router
from backend.src.core.config import settings
from backend.src.utils.logger import get_logger
from backend.src.core.container import app_state

logger = get_logger(__name__)

app = FastAPI(
    title="Darwinistic Evolution Simulator",
    description="Backend for simulating creature evolution.",
    version="0.1.0",
)

@app.on_event("startup")
async def startup_event():
    """Attaches the application state to the app instance on startup."""
    app.state.app_state = app_state
    logger.info("Application startup complete. Initialized state.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(simulation_router, prefix="/api/v1")

@app.get("/health", tags=["Monitoring"])
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.APP_PORT,
        reload=True,
        log_level=settings.LOG_LEVEL.lower(),
    )
