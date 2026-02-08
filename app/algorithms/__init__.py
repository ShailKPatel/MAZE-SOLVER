from .bfs import solve_bfs
from .dfs import solve_dfs

from .bidirectional import solve_bidirectional_bfs
from .greedy import solve_greedy
from .astar import solve_astar

ALGORITHMS = {
    "BFS": solve_bfs,
    "DFS": solve_dfs,

    "Bidirectional BFS": solve_bidirectional_bfs,
    "Greedy Best-First Search": solve_greedy,
    "A*": solve_astar
}
