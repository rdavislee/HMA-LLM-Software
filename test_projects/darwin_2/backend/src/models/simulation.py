from typing import List, Optional

from backend.src.models.creature import Creature
from pydantic import BaseModel, Field

class SimulationSettings(BaseModel):
    population_size: int = Field(50, gt=0, description="Number of creatures per generation.")
    generations: int = Field(100, gt=0, description="Number of generations to simulate.")
    mutation_rate: float = Field(0.01, ge=0, le=1, description="Rate of mutation for offspring.")
    gravity: float = Field(-9.81, description="Gravitational force in the simulation.")

class SimulationRequest(BaseModel):
    settings: SimulationSettings

class SimulationResponse(BaseModel):
    job_id: str
    status: str
    message: Optional[str] = None

class GenerationResult(BaseModel):
    generation_number: int
    best_fitness: float
    average_fitness: float
    top_creature: Optional[Creature] = None

class SimulationResult(BaseModel):
    job_id: str
    status: str
    settings: SimulationSettings
    results: List[GenerationResult]
