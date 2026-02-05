import random
from collections import deque
from .models import MazeConfig, MazeState

def generate_maze(config: MazeConfig) -> MazeState:
    # 1. Determine Start/End
    # Start: Must be inside (not on boundary)
    rows, cols = config.height, config.width
    
    start_r = random.randint(1, rows - 2)
    start_c = random.randint(1, cols - 2)
    start_pos = (start_r, start_c)
    
    # End: Must be on boundary
    # 0=Top, 1=Bottom, 2=Left, 3=Right
    side = random.randint(0, 3) 
    if side == 0:   # Top
        end_pos = (0, random.randint(0, cols - 1))
    elif side == 1: # Bottom
        end_pos = (rows - 1, random.randint(0, cols - 1))
    elif side == 2: # Left
        end_pos = (random.randint(0, rows - 1), 0)
    else:           # Right
        end_pos = (random.randint(0, rows - 1), cols - 1)
        
    # Ensure start != end (Implicitly true as start is inside and end is boundary)
    # But just in case dimensions are tiny (e.g. 3x3), start is (1,1). End could be (0,1).
    # They won't overlap.

    # 2. Generate Grid
    # Strategy:
    # - If unique_path or not allow_cycles => Recursive Backtracker (Perfect Maze)
    # - Else => Random Noise based on wall_density
    
    rows, cols = config.height, config.width
    grid = [[1 for _ in range(cols)] for _ in range(rows)] # Initialize with Walls (1)

    if config.unique_path or not config.allow_cycles:
        # Recursive Backtracker
        # Start at random point or start_pos
        # We need odd coordinates for walls/paths to look nice in traditional maze gen, 
        # but here we have arbitrary size. We'll simply carve.
        # Actually pure backtracker works best on odd grids with (1,1) start.
        # We will adapt: Treat grid as cells and walls. 
        # Simplest: Randomized DFS carving.
        
        stack = [start_pos]
        visited = set([start_pos])
        grid[start_pos[0]][start_pos[1]] = 2
        
        # Directions: Up, Down, Left, Right
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        # Simple R-DFS often creates low branching factor. 
        # For "dead end density", we could vary the probability of popping or branching.
        # But for now, standard shuffle.
        
        # NOTE: To create a "Perfect Maze" where walls are 1-thick, we usually step by 2.
        # But our grid is dense. 
        # If we step 1, we get open caverns if we visit neighbors.
        # Let's use the "Step by 2" logic if possible, but map to our grid.
        # Or simpler: Randomized Prim's or just Random Traversal on dense grid 
        # ensuring we leave walls.
        # Let's stick to: Carve from Start.
        
        # To strictly enforce "No Cycles" on a dense grid, we just never carve into an already visited cell (value 2).
        # We only carve into 1s.
        
        # Wait, if we just carve into 1s, we might make a 2x2 block of open space?
        # Yes. To avoid "thick paths" (which are effectively cycles on a pixel level), 
        # we need to check diagonals or 2-step neighbors.
        # Let's try "Carve to neighbor if neighbor has > 1 solid neighbor"? 
        # That logic keeps walls thin.
        
        # Let's try a standard approach for dense arrays:
        # "Grow path". 
        
        # Actually, if the user asks for "Wall Density 10%" and "No Cycles", that's impossible.
        # A tree covering the grid implies a certain density.
        # I will PRIORITIZE the "Structure" (Cycles/Unique) over "Density" slider in this mode.
        
        # Generating a Perfect Maze (Spanning Tree):
        # We'll use a helper set to track visited "nodes".
        # But since we don't have a rigid "cell vs wall" coordinate system enforced by the inputs (user can give 10x10),
        # implementation of a perfect maze on even dimensions is tricky.
        # We will attempt a "Randomized Prim's" generalized.
        
        walls = []
        # Start cell
        grid[start_pos[0]][start_pos[1]] = 2
        
        # Add neighbors to wall list
        for dr, dc in directions:
            nr, nc = start_pos[0] + dr, start_pos[1] + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                walls.append((nr, nc, start_pos[0], start_pos[1]))
                
        while walls:
            # Pick random wall
            idx = random.randint(0, len(walls) - 1)
            r, c, pr, pc = walls[idx] # current, parent
            
            # If current is wall (1)
            if grid[r][c] == 1:
                # Check if it has only one visited neighbor (the parent). 
                # Actually, in Prim's on dense grid, we check if it connects to "Visited" and "Unvisited".
                # But here 'r,c' is an unvisited cell. 
                # We want to maintain thin walls.
                # A safe heuristic for "Thin Walls (Tree)" on dense grid:
                # Count 8-neighbors (including diagonals) that are OPEN (2).
                # If count <= 1 (only the parent path we are coming from), then SAFE to open.
                # Wait, diagonals? 
                
                open_neighbors = 0
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if dr == 0 and dc == 0: continue
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < rows and 0 <= nc < cols:
                            if grid[nr][nc] == 2:
                                open_neighbors += 1
                                
                # If we rely on stored parent, we know 1 is open.
                # If open_neighbors <= 2 (Parent + maybe a diagonal touch?), it's safer.
                # Strictly < 2 (only existing parent) prevents 2x2 blobs. 
                # But this is too restrictive, might get stuck.
                
                # Let's use simple logic: Only open if 4-neighbors count == 1.
                cardinal_open = 0
                for dr, dc in directions:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols:
                        if grid[nr][nc] == 2:
                            cardinal_open += 1
                            
                if cardinal_open == 1:
                    grid[r][c] = 2
                    walls.pop(idx)
                    # Add new neighbors
                    for dr, dc in directions:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < rows and 0 <= nc < cols:
                            if grid[nr][nc] == 1:
                                walls.append((nr, nc, r, c))
                else:
                    walls.pop(idx)
            else:
                walls.pop(idx)
                
    else:
        # Random Noise Mode (Cycles allowed)
        # Use wall_density directly
        for r in range(rows):
            for c in range(cols):
                if random.random() > config.wall_density:
                    grid[r][c] = 2 # Empty
                else:
                    grid[r][c] = 1 # Wall
                    
        # Ensure start/end are open
        grid[start_pos[0]][start_pos[1]] = 2
        grid[end_pos[0]][end_pos[1]] = 2

    # 3. Apply Constraints (Guaranteed Path, No Path)
    
    # Helper BFS
    def get_path():
        q = deque([start_pos])
        seen = {start_pos}
        parent = {start_pos: None}
        
        while q:
            curr = q.popleft()
            if curr == end_pos:
                path = []
                while curr:
                    path.append(curr)
                    curr = parent[curr]
                return path[::-1]
            
            for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                nr, nc = curr[0]+dr, curr[1]+dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    if grid[nr][nc] != 1 and (nr, nc) not in seen:
                        seen.add((nr, nc))
                        parent[(nr, nc)] = curr
                        q.append((nr, nc))
        return None

    path = get_path()
    
    if config.no_path:
        # We need NO path.
        if path:
            # Block it.
            # Simple approach: Block a random cell on the path (excluding start/end)
            if len(path) > 2:
                to_block = path[random.randint(1, len(path)-2)]
                grid[to_block[0]][to_block[1]] = 1
                # Check again. If still path, repeat?
                # The path might bypass.
                # Better: Flood fill from Start. Create boundary of walls?
                # Simplest: Just re-run get_path loop max N times blocking things.
                for _ in range(50): # attempts
                    p2 = get_path()
                    if not p2: break
                    if len(p2) > 2:
                        # Block middle
                        mb = p2[len(p2)//2]
                        grid[mb[0]][mb[1]] = 1
                        
        grid[start_pos[0]][start_pos[1]] = 10
        grid[end_pos[0]][end_pos[1]] = 11
        return MazeState(width=cols, height=rows, grid=grid, start_pos=start_pos, end_pos=end_pos)

    if config.guaranteed_path:
        # We MUST have a path.
        if not path:
            # Cheat: Carve a random walk or geometric path from Start to End.
            # "Drunkard's Walk" guided towards End.
            curr = start_pos
            while curr != end_pos:
                grid[curr[0]][curr[1]] = 2
                # Choose direction that moves closer?
                # Or just A* with ignoring walls?
                # Let's do a simple "move closer" logic with randomness.
                
                r, c = curr
                tr, tc = end_pos
                
                opts = []
                for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                    nr, nc = r+dr, c+dc
                    if 0 <= nr < rows and 0 <= nc < cols:
                        opts.append((nr, nc))
                
                # Sort opts by distance to end
                opts.sort(key=lambda p: abs(p[0]-tr) + abs(p[1]-tc))
                
                # Pick best with high prob, or random
                if random.random() < 0.7:
                    next_step = opts[0]
                else:
                    next_step = random.choice(opts)
                
                curr = next_step
            
            grid[end_pos[0]][end_pos[1]] = 2
            
    grid[start_pos[0]][start_pos[1]] = 10
    grid[end_pos[0]][end_pos[1]] = 11
    return MazeState(width=cols, height=rows, grid=grid, start_pos=start_pos, end_pos=end_pos)
