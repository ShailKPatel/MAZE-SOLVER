from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
from pydantic import BaseModel
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


from .models import MazeConfig, MazeState, SolveRequest, StepUpdate
from .maze_generator import generate_maze
from .algorithms import ALGORITHMS

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/generate", response_model=MazeState)
def generate_maze_endpoint(config: MazeConfig):
    return generate_maze(config)

@app.post("/api/solve", response_model=List[StepUpdate])
def solve_maze_endpoint(request: SolveRequest):
    if request.algorithm not in ALGORITHMS:
        raise HTTPException(status_code=400, detail="Algorithm not found")
    
    solver = ALGORITHMS[request.algorithm]
    # Run the generator to completion and return all steps
    steps = list(solver(request.maze))
    return steps

class BatchConfig(BaseModel):
    maze_config: MazeConfig
    num_mazes: int
    algorithms: List[str]

class BatchResult(BaseModel):
    algorithm: str
    success_rate: float
    avg_time_ms: float
    avg_nodes: float
    avg_path_length: float
    avg_steps: float
    avg_frontier: float

@app.post("/api/batch", response_model=List[BatchResult])
def batch_simulation(config: BatchConfig):
    results = {algo: {"success": 0, "time": 0.0, "nodes": 0, "path_len": 0, "steps": 0, "frontier": 0, "count": 0} for algo in config.algorithms}
    
    for _ in range(config.num_mazes):
        # Generate one maze for all algos to ensure fair comparison
        maze = generate_maze(config.maze_config)
        
        for algo_name in config.algorithms:
            if algo_name not in ALGORITHMS: continue
            
            solver = ALGORITHMS[algo_name]
            start_time = time.perf_counter()
            
            # Run solver (non-generator mode would be faster but we reuse logic)
            # We iterate to end
            steps_list = list(solver(maze))
            
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            
            if not steps_list: continue
            last_step = steps_list[-1]
            
            res = results[algo_name]
            res["count"] += 1
            res["time"] += duration_ms
            res["nodes"] += last_step.nodes_expanded
            res["steps"] += last_step.steps_taken
            res["frontier"] += last_step.max_frontier_size
            
            if last_step.success:
                res["success"] += 1
                res["path_len"] += last_step.path_length

    # Aggregation
    final_output = []
    for algo, data in results.items():
        count = data["count"]
        if count == 0: continue
        
        final_output.append(BatchResult(
            algorithm=algo,
            success_rate=data["success"] / count,
            avg_time_ms=data["time"] / count,
            avg_nodes=data["nodes"] / count,
            avg_path_length=data["path_len"] / data["success"] if data["success"] > 0 else 0,
            avg_steps=data["steps"] / count,
            avg_frontier=data["frontier"] / count
        ))
        
    return final_output

@app.get("/health")
def health_check():
    return {"status": "ok"}

# Mount static last so API takes precedence
STATIC_DIR = BASE_DIR / "static"
app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
