from typing import List, Optional, Tuple

from pydantic import BaseModel, Field

class Node(BaseModel):
    id: int
    position: Tuple[float, float]

class Muscle(BaseModel):
    id: int
    nodes: Tuple[int, int] # Connects two node IDs
    length: float
    stiffness: float

class Brain(BaseModel):
    weights: List[float]

class Creature(BaseModel):
    id: int
    nodes: List[Node]
    muscles: List[Muscle]
    brain: Brain
    fitness: Optional[float] = None
