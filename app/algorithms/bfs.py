from collections import deque
from ..models import MazeState, StepUpdate
from .utils import reconstruct_path, get_neighbors

def solve_bfs(state: MazeState):
    start = state.start_pos
    end = state.end_pos
    
    queue = deque([start])
    visited = {start}
    parent = {start: None}
    
    nodes_expanded = 0
    steps = 0
    
    max_frontier_size = 1 # Initial queue
    
    # Initial Step
    yield StepUpdate(
        grid_updates=[(start[0], start[1], 3)], 
        current_cell=start, 
        nodes_expanded=0,
        steps_taken=0,
        max_frontier_size=max_frontier_size
    )
    
    while queue:
        current = queue.popleft()
        nodes_expanded += 1
        steps += 1
        
        updates = [(current[0], current[1], 4)]
        
        if current == end:
            # Found!
            path = reconstruct_path(parent, end)
            path_updates = [(r, c, 5) for r, c in path]
            yield StepUpdate(
                grid_updates=path_updates,
                finished=True,
                success=True,
                path_length=len(path),
                nodes_expanded=nodes_expanded,
                steps_taken=steps,
                max_frontier_size=max_frontier_size
            )
            return

        neighbors = get_neighbors(state, current)
        for next_node in neighbors:
            if next_node not in visited:
                visited.add(next_node)
                parent[next_node] = current
                queue.append(next_node)
                updates.append((next_node[0], next_node[1], 3)) # Add to frontier
        
        max_frontier_size = max(max_frontier_size, len(queue))
        
        yield StepUpdate(
            grid_updates=updates,
            current_cell=current,
            nodes_expanded=nodes_expanded,
            steps_taken=steps,
            max_frontier_size=max_frontier_size
        )

    # Not found
    yield StepUpdate(finished=True, success=False, nodes_expanded=nodes_expanded, steps_taken=steps, max_frontier_size=max_frontier_size)
