from collections import deque
from ..models import MazeState, StepUpdate
from .utils import reconstruct_path, get_neighbors

def solve_bidirectional_bfs(state: MazeState):
    start = state.start_pos
    end = state.end_pos
    
    q_start = deque([start])
    q_end = deque([end])
    
    visited_start = {start}
    visited_end = {end}
    
    parent_start = {start: None}
    parent_end = {end: None}
    
    nodes_expanded = 0
    steps = 0
    max_frontier_size = 2
    
    yield StepUpdate(grid_updates=[(start[0], start[1], 3), (end[0], end[1], 3)], current_cell=start, nodes_expanded=0, steps_taken=0, max_frontier_size=max_frontier_size)
    
    while q_start and q_end:
        max_frontier_size = max(max_frontier_size, len(q_start) + len(q_end))
        # Expand from start
        if q_start:
            curr_s = q_start.popleft()
            nodes_expanded += 1
            steps += 1
            
            # Check intersection
            if curr_s in visited_end:
                # Meeting point found!
                path_s = reconstruct_path(parent_start, curr_s)
                path_e = reconstruct_path(parent_end, curr_s)
                path = path_s + path_e[::-1][1:] # join paths
                
                yield StepUpdate(
                    grid_updates=[(r,c,5) for r,c in path],
                    finished=True, success=True, path_length=len(path), nodes_expanded=nodes_expanded, steps_taken=steps, max_frontier_size=max_frontier_size
                )
                return

            updates = [(curr_s[0], curr_s[1], 4)]
            
            for neighbor in get_neighbors(state, curr_s):
                if neighbor not in visited_start:
                    visited_start.add(neighbor)
                    parent_start[neighbor] = curr_s
                    q_start.append(neighbor)
                    updates.append((neighbor[0], neighbor[1], 3))
            
            yield StepUpdate(grid_updates=updates, current_cell=curr_s, nodes_expanded=nodes_expanded, steps_taken=steps, max_frontier_size=max_frontier_size)

        # Expand from end
        if q_end:
            curr_e = q_end.popleft()
            nodes_expanded += 1
            steps += 1
            
            # Check intersection
            if curr_e in visited_start:
                # Meeting point found
                path_s = reconstruct_path(parent_start, curr_e)
                path_e = reconstruct_path(parent_end, curr_e)
                path = path_s + path_e[::-1][1:]
                
                yield StepUpdate(
                    grid_updates=[(r,c,5) for r,c in path],
                    finished=True, success=True, path_length=len(path), nodes_expanded=nodes_expanded, steps_taken=steps, max_frontier_size=max_frontier_size
                )
                return

            updates = [(curr_e[0], curr_e[1], 4)]
            
            for neighbor in get_neighbors(state, curr_e):
                if neighbor not in visited_end:
                    visited_end.add(neighbor)
                    parent_end[neighbor] = curr_e
                    q_end.append(neighbor)
                    updates.append((neighbor[0], neighbor[1], 3))
            
            yield StepUpdate(grid_updates=updates, current_cell=curr_e, nodes_expanded=nodes_expanded, steps_taken=steps, max_frontier_size=max_frontier_size)

    yield StepUpdate(finished=True, success=False, nodes_expanded=nodes_expanded, steps_taken=steps, max_frontier_size=max_frontier_size)
