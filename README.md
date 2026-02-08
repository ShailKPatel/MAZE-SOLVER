# Maze Solver Walkthrough

## Overview
The Maze Solver is a two-page web application built with **FastAPI** (Backend) and **Vanilla JS + Tailwind CSS** (Frontend). It visualizes various pathfinding algorithms on generated mazes and allows for batch analysis.

## Features
- **Interactive Solver**: Generate random mazes with constraints (Cycles, Density) and visualize algorithms (BFS, DFS, A*, etc.) step-by-step.
- **Batch Analysis**: Run simulations on hundreds of mazes to compare algorithm performance (Success rate, Time, Nodes expanded).
- **Algorithms**: BFS, DFS, Dijkstra, A*, Greedy Best-First.

## Implementation Details
- **Backend**: `app/main.py` serves the API and static files. `app/algorithms.py` implements the solvers as generators. `app/maze_generator.py` handles maze creation.
- **Frontend**: `app/static/index.html` uses an HTML5 Canvas for high-performance rendering. `app/static/script.js` manages the simulation loop.

## How to Run

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Server**:
   ```bash
   uvicorn app.main:app --reload
   ```

3. **Access the App**:
   Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

## Deployment
This application is ready for deployment on Render, Railway, or Fly.io.
- Ensure `requirements.txt` is present.
- The start command is `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.

## Verification Results
- **Syntax Check**: All Python files passed compilation checks.
- **App Structure**: Valid FastAPI structure with static mounting.
- **Front-End**: `index.html` and `batch.html` are linked and set up with Tailwind CDN.

## Next Steps
- Open the application in a browser.
- Adjust the "Grid Configuration" sliders.
- Click "Generate New" to create a maze.
- Select an algorithm and click "Run".
- Visit "Batch Analysis" to compare performance stats.
