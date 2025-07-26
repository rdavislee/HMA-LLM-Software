from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.api.endpoints import router as api_router

app = FastAPI()

app.include_router(api_router, prefix="/api")

app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")

@app.get("/")
async def root():
    return {"message": "Welcome to the Evolution Simulator API. Navigate to /docs for API documentation."}
