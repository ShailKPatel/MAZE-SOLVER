from pydantic import BaseModel, Field
from typing import List, Optional, Tuple

class MazeConfig(BaseModel):
    width: int = Field(..., ge=5, le=100)
    height: int = Field(..., ge=5, le=100)
    wall_density: float = Field(0.3, ge=0.0, le=1.0)
    
    start_fixed: bool = True
    end_fixed: bool = True
    
    # Path Constraints
    guaranteed_path: bool = True
    no_path: bool = False
    unique_path: bool = False
    allow_cycles: bool = False
    
    # dead_end_density isn't easily directly controllable in all generation algorithms
    # but we will accept it as a parameter to influence generation if possible
    dead_end_density: float = Field(0.5, ge=0.0, le=1.0)

class MazeState(BaseModel):
    width: int
    height: int
    grid: List[List[int]] # 1=Wall, 2=Empty, 3=Exploring, 4=Dead, 5=Path
    start_pos: Tuple[int, int]
    end_pos: Tuple[int, int]

class SolveRequest(BaseModel):
    maze: MazeState
    algorithm: str

class StepUpdate(BaseModel):
    grid_updates: List[Tuple[int, int, int]] = Field(default_factory=list) # (row, col, new_val)
    current_cell: Optional[Tuple[int, int]] = None
    finished: bool = False
    success: bool = False
    path_length: int = 0
    nodes_expanded: int = 0
