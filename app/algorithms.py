import heapq
from collections import deque
from .models import MazeState, StepUpdate

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

def solve_bfs(state: MazeState):
    start = state.start_pos
    end = state.end_pos
    
    queue = deque([start])
    visited = {start}
    parent = {start: None}
    
    nodes_expanded = 0
    steps = 0
    
    # Initial Step
    yield StepUpdate(
        grid_updates=[(start[0], start[1], 3)], 
        current_cell=start, 
        nodes_expanded=0
    )
    
    while queue:
        current = queue.popleft()
        nodes_expanded += 1
        steps += 1
        
        # Visual update: Mark current as "visited/closed" (maybe stay 3 or turn light yellow?)
        # Specification says: 3 = Currently exploring, 4 = Dead path.
        # We'll mark OLD current as 4 (Visited) or keep 3?
        # Actually usually: 3 = Frontier/Active. 4 = Closed?
        # Specification: "2=Empty, 3=Exploring, 4=Dead path (visited, no solution through this cell)"
        # "Dead path" usually means we backtracked. In BFS, everything visited is "Dead" unless it's the path.
        # Let's say Visited = 4. Active = 3.
        
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
                nodes_expanded=nodes_expanded
            )
            return

        neighbors = get_neighbors(state, current)
        for next_node in neighbors:
            if next_node not in visited:
                visited.add(next_node)
                parent[next_node] = current
                queue.append(next_node)
                updates.append((next_node[0], next_node[1], 3)) # Add to frontier
        
        yield StepUpdate(
            grid_updates=updates,
            current_cell=current,
            nodes_expanded=nodes_expanded
        )

    # Not found
    yield StepUpdate(finished=True, success=False, nodes_expanded=nodes_expanded)


def solve_dfs(state: MazeState):
    start = state.start_pos
    end = state.end_pos
    
    stack = [start]
    visited = {start} # Visited implies "Processed or in Stack"
    parent = {start: None}
    
    nodes_expanded = 0
    
    yield StepUpdate(grid_updates=[(start[0], start[1], 3)], current_cell=start)

    while stack:
        current = stack.pop()
        nodes_expanded += 1
        
        # Mark as visited (Dead/Closed) locally, but in DFS "Active" is the tip of stack.
        updates = [(current[0], current[1], 4)]

        if current == end:
            path = reconstruct_path(parent, end)
            path_updates = [(r, c, 5) for r, c in path]
            yield StepUpdate(
                grid_updates=path_updates,
                finished=True,
                success=True,
                path_length=len(path),
                nodes_expanded=nodes_expanded
            )
            return

        neighbors = get_neighbors(state, current)
        # Randomize neighbor order or fixed? Fixed is fine.
        # For DFS to look "right", we usually add neighbors to stack.
        
        added_children = False
        for next_node in neighbors:
            if next_node not in visited:
                visited.add(next_node)
                parent[next_node] = current
                stack.append(next_node)
                updates.append((next_node[0], next_node[1], 3))
                added_children = True
        
        yield StepUpdate(
            grid_updates=updates,
            current_cell=current,
            nodes_expanded=nodes_expanded
        )

    yield StepUpdate(finished=True, success=False, nodes_expanded=nodes_expanded)


def solve_dijkstra(state: MazeState):
    # Valid for unweighted or weighted. Here unweighted -> behaves like BFS but slightly different order if weights existed.
    start = state.start_pos
    end = state.end_pos
    
    # Priority Queue: (cost, node)
    pq = [(0, start)]
    visited = {} # node -> cost
    parent = {start: None}
    visited[start] = 0
    
    nodes_expanded = 0
    
    yield StepUpdate(grid_updates=[(start[0], start[1], 3)], current_cell=start)
    
    while pq:
        cost, current = heapq.heappop(pq)
        nodes_expanded += 1
        
        if current == end:
            path = reconstruct_path(parent, end)
            yield StepUpdate(
                grid_updates=[(r,c,5) for r,c in path],
                finished=True, success=True, path_length=len(path), nodes_expanded=nodes_expanded
            )
            return
            
        updates = [(current[0], current[1], 4)]
        
        neighbors = get_neighbors(state, current)
        for next_node in neighbors:
            new_cost = cost + 1
            if next_node not in visited or new_cost < visited[next_node]:
                visited[next_node] = new_cost
                parent[next_node] = current
                heapq.heappush(pq, (new_cost, next_node))
                updates.append((next_node[0], next_node[1], 3))
                
        yield StepUpdate(grid_updates=updates, current_cell=current, nodes_expanded=nodes_expanded)

    yield StepUpdate(finished=True, success=False, nodes_expanded=nodes_expanded)


def solve_astar(state: MazeState):
    start = state.start_pos
    end = state.end_pos
    
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
        
    pq = [(0, start)] # (f_score, node)
    g_score = {start: 0}
    parent = {start: None}
    
    nodes_expanded = 0
    
    yield StepUpdate(grid_updates=[(start[0], start[1], 3)], current_cell=start)
    
    while pq:
        _, current = heapq.heappop(pq)
        nodes_expanded += 1
        
        if current == end:
            path = reconstruct_path(parent, end)
            yield StepUpdate(
                grid_updates=[(r,c,5) for r,c in path],
                finished=True, success=True, path_length=len(path), nodes_expanded=nodes_expanded
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
                
        yield StepUpdate(grid_updates=updates, current_cell=current, nodes_expanded=nodes_expanded)

    yield StepUpdate(finished=True, success=False, nodes_expanded=nodes_expanded)

def solve_greedy(state: MazeState):
    start = state.start_pos
    end = state.end_pos
    
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    # Priority Queue: (h_score, node) - Only heuristic matters
    pq = [(heuristic(start, end), start)]
    visited = {start}
    parent = {start: None}
    
    nodes_expanded = 0
    yield StepUpdate(grid_updates=[(start[0], start[1], 3)], current_cell=start)
    
    while pq:
        _, current = heapq.heappop(pq)
        nodes_expanded += 1
        
        if current == end:
            path = reconstruct_path(parent, end)
            yield StepUpdate(
                grid_updates=[(r,c,5) for r,c in path],
                finished=True, success=True, path_length=len(path), nodes_expanded=nodes_expanded
            )
            return
        
        updates = [(current[0], current[1], 4)]
        
        neighbors = get_neighbors(state, current)
        # Sort neighbors by h to break ties? Not strictly needed with heap.
        
        for neighbor in neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = current
                h = heuristic(neighbor, end)
                heapq.heappush(pq, (h, neighbor))
                updates.append((neighbor[0], neighbor[1], 3))
                
        yield StepUpdate(grid_updates=updates, current_cell=current, nodes_expanded=nodes_expanded)

    yield StepUpdate(finished=True, success=False, nodes_expanded=nodes_expanded)


def solve_iddfs(state: MazeState):
    start = state.start_pos
    end = state.end_pos
    nodes_expanded = 0
    
    # Helper DLS
    def dls(current, depth, path_set, history_parent):
        nonlocal nodes_expanded
        nodes_expanded += 1
        
        # Visualization: Mark current as exploring (3)
        # For IDDFS, we re-visit nodes. 
        # We need to emit update.
        yield StepUpdate(
            grid_updates=[(current[0], current[1], 3)], 
            current_cell=current, 
            nodes_expanded=nodes_expanded
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
        # We clean up visualization between depths? 
        # Ideally yes, but IDDFS is messy. We'll just let it overwrite.
        path_set = {start}
        parent_map = {}
        
        # Generator delegation
        result = yield from dls(start, depth, path_set, parent_map)
        
        if result:
            final_path = result[::-1]
            yield StepUpdate(
                grid_updates=[(r,c,5) for r,c in final_path],
                finished=True, success=True, path_length=len(final_path), nodes_expanded=nodes_expanded
            )
            return
            
    yield StepUpdate(finished=True, success=False, nodes_expanded=nodes_expanded)


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
    
    yield StepUpdate(grid_updates=[(start[0], start[1], 3), (end[0], end[1], 3)], current_cell=start, nodes_expanded=0)
    
    while q_start and q_end:
        # Expand from start
        if q_start:
            curr_s = q_start.popleft()
            nodes_expanded += 1
            
            # Check intersection
            if curr_s in visited_end:
                # Meeting point found!
                path_s = reconstruct_path(parent_start, curr_s)
                path_e = reconstruct_path(parent_end, curr_s)
                path = path_s + path_e[::-1][1:] # join paths
                
                yield StepUpdate(
                    grid_updates=[(r,c,5) for r,c in path],
                    finished=True, success=True, path_length=len(path), nodes_expanded=nodes_expanded
                )
                return

            updates = [(curr_s[0], curr_s[1], 4)]
            
            for neighbor in get_neighbors(state, curr_s):
                if neighbor not in visited_start:
                    visited_start.add(neighbor)
                    parent_start[neighbor] = curr_s
                    q_start.append(neighbor)
                    updates.append((neighbor[0], neighbor[1], 3))
            
            yield StepUpdate(grid_updates=updates, current_cell=curr_s, nodes_expanded=nodes_expanded)

        # Expand from end
        if q_end:
            curr_e = q_end.popleft()
            nodes_expanded += 1
            
            # Check intersection
            if curr_e in visited_start:
                # Meeting point found
                path_s = reconstruct_path(parent_start, curr_e)
                path_e = reconstruct_path(parent_end, curr_e)
                path = path_s + path_e[::-1][1:]
                
                yield StepUpdate(
                    grid_updates=[(r,c,5) for r,c in path],
                    finished=True, success=True, path_length=len(path), nodes_expanded=nodes_expanded
                )
                return

            updates = [(curr_e[0], curr_e[1], 4)]
            
            for neighbor in get_neighbors(state, curr_e):
                if neighbor not in visited_end:
                    visited_end.add(neighbor)
                    parent_end[neighbor] = curr_e
                    q_end.append(neighbor)
                    updates.append((neighbor[0], neighbor[1], 3))
            
            yield StepUpdate(grid_updates=updates, current_cell=curr_e, nodes_expanded=nodes_expanded)

    yield StepUpdate(finished=True, success=False, nodes_expanded=nodes_expanded)


ALGORITHMS = {
    "BFS": solve_bfs,
    "DFS": solve_dfs,
    "Iterative Deepening DFS": solve_iddfs,
    "Bidirectional BFS": solve_bidirectional_bfs,
    "Greedy Best-First Search": solve_greedy, # Renamed to match user request
    "A*": solve_astar
}
