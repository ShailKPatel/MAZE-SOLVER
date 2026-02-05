from ..models import MazeState

# Helper to reconstruct path
def reconstruct_path(parent, current):
    path = []
    while current:
        path.append(current)
        current = parent.get(current)
    return path[::-1]

def get_neighbors(state: MazeState, node):
    r, c = node
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    result = []
    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        if 0 <= nr < state.height and 0 <= nc < state.width:
            # 1 is Wall
            if state.grid[nr][nc] != 1:
                result.append((nr, nc))
    return result
