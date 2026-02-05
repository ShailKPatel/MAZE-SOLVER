import heapq
from ..models import MazeState, StepUpdate
from .utils import reconstruct_path, get_neighbors

def solve_astar(state: MazeState):
    start = state.start_pos
    end = state.end_pos
    
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
        
    pq = [(0, start)] # (f_score, node)
    g_score = {start: 0}
    parent = {start: None}
    
    nodes_expanded = 0
    steps = 0
    max_frontier_size = 1
    
    yield StepUpdate(grid_updates=[(start[0], start[1], 3)], current_cell=start, max_frontier_size=max_frontier_size)
    
    while pq:
        _, current = heapq.heappop(pq)
        nodes_expanded += 1
        
        if current == end:
            path = reconstruct_path(parent, end)
            yield StepUpdate(
                grid_updates=[(r,c,5) for r,c in path],
                finished=True, success=True, path_length=len(path), nodes_expanded=nodes_expanded, steps_taken=steps, max_frontier_size=max_frontier_size
            )
            return
            
        updates = [(current[0], current[1], 4)]
        
        for neighbor in get_neighbors(state, current):
            tentative_g = g_score[current] + 1
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                g_score[neighbor] = tentative_g
                f_score = tentative_g + heuristic(neighbor, end)
                heapq.heappush(pq, (f_score, neighbor))
                parent[neighbor] = current
                updates.append((neighbor[0], neighbor[1], 3))
                
        steps += 1
        max_frontier_size = max(max_frontier_size, len(pq))
        yield StepUpdate(grid_updates=updates, current_cell=current, nodes_expanded=nodes_expanded, steps_taken=steps, max_frontier_size=max_frontier_size)

    yield StepUpdate(finished=True, success=False, nodes_expanded=nodes_expanded, steps_taken=steps, max_frontier_size=max_frontier_size)
