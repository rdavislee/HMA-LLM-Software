import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    
    # Simulation Defaults
    DEFAULT_POPULATION_SIZE: int = 50
    DEFAULT_GENERATIONS: int = 100
    DEFAULT_MUTATION_RATE: float = 0.01
    DEFAULT_GRAVITY: float = -9.81
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
