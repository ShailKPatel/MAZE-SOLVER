from ..models import MazeState, StepUpdate
from .utils import reconstruct_path, get_neighbors

def solve_iddfs(state: MazeState):
    start = state.start_pos
    end = state.end_pos
    nodes_expanded = 0
    steps = 0
    max_frontier_size = 0 # Updates with depth
    
    # Helper DLS
    def dls(current, depth, path_set, history_parent):
        nonlocal nodes_expanded, steps
        nodes_expanded += 1
        steps += 1
        
        # Visualization: Mark current as exploring (3)
        yield StepUpdate(
            grid_updates=[(current[0], current[1], 3)], 
            current_cell=current, 
            nodes_expanded=nodes_expanded,
            steps_taken=steps,
            max_frontier_size=max_frontier_size
        )
        
        if current == end:
            return [current]
        
        if depth <= 0:
            # Backtracking (mark as dead for this iteration?)
            yield StepUpdate(grid_updates=[(current[0], current[1], 4)], current_cell=current)
            return None
        
        neighbors = get_neighbors(state, current)
        for neighbor in neighbors:
            if neighbor not in path_set:
                path_set.add(neighbor)
                history_parent[neighbor] = current
                
                path = yield from dls(neighbor, depth - 1, path_set, history_parent)
                if path:
                    path.append(current)
                    return path
                
                path_set.remove(neighbor)
        
        # If all neighbors fail, mark current as dead for this branch
        yield StepUpdate(grid_updates=[(current[0], current[1], 4)], current_cell=current)
        return None

    # Iterative Deepening
    max_depth = state.width * state.height # Safe upper bound
    
    for depth in range(max_depth):
        max_frontier_size = depth
        # We clean up visualization between depths
        path_set = {start}
        parent_map = {}
        
        # Generator delegation
        result = yield from dls(start, depth, path_set, parent_map)
        
        if result:
            final_path = result[::-1]
            yield StepUpdate(
                grid_updates=[(r,c,5) for r,c in final_path],
                finished=True, success=True, path_length=len(final_path), nodes_expanded=nodes_expanded, steps_taken=steps, max_frontier_size=max_frontier_size
            )
            return
            
    yield StepUpdate(finished=True, success=False, nodes_expanded=nodes_expanded, steps_taken=steps, max_frontier_size=max_frontier_size)
