const ALGO_INFO = {
    "BFS": {
        title: "Breadth-First Search (BFS)",
        desc: "Breadth-First Search explores all neighbor nodes at the present depth prior to moving on to the nodes at the next depth level.",
        code: `def bfs(graph, start):
    queue = [start]
    while queue:
        vertex = queue.pop(0)
        # Process vertex
        for neighbor in graph[vertex]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)`
    },
    "DFS": {
        title: "Depth-First Search (DFS)",
        desc: "Explores as far as possible along each branch before backtracking.",
        code: `def dfs(graph, start, visited=None):
    if visited is None:
        visited = set()
    visited.add(start)
    for next in graph[start] - visited:
        dfs(graph, next, visited)
    return visited`
    },
    "Iterative Deepening DFS": {
        title: "Iterative Deepening DFS (IDDFS)",
        desc: "Combines depth-first search's space-efficiency and breadth-first search's completeness.",
        code: `def iddfs(graph, start, goal):
    depth = 0
    while True:
        result = dls(start, goal, depth)
        if result == 'found': return result
        depth += 1

def dls(node, goal, depth):
    if depth == 0 and node == goal: return 'found'
    if depth > 0:
        for neighbor in graph[node]:
            if dls(neighbor, goal, depth-1) == 'found':
                return 'found'
    return None`
    },
    "Bidirectional BFS": {
        title: "Bidirectional BFS",
        desc: "Runs two simultaneous breadth-first searches: one from the start node and one from the goal node.",
        code: `def bidirectional_bfs(graph, start, goal):
    if start == goal: return [start]
    
    start_queue = [start]
    goal_queue = [goal]
    start_visited = {start}
    goal_visited = {goal}
    
    while start_queue and goal_queue:
        # Expand start side
        if bfs_step(start_queue, start_visited, goal_visited):
             return "Path Found"
        # Expand goal side
        if bfs_step(goal_queue, goal_visited, start_visited):
             return "Path Found"
    return "No Path"
    
def bfs_step(queue, visited, other_visited):
    curr = queue.pop(0)
    for neighbor in graph[curr]:
        if neighbor in other_visited: return True
        if neighbor not in visited:
            visited.add(neighbor)
            queue.append(neighbor)
    return False`
    },
    "Greedy Best-First Search": {
        title: "Greedy Best-First Search",
        desc: "Expands the node that is estimated to be closest to the goal.",
        code: `def greedy_bfs(graph, start, goal):
    pq = PriorityQueue()
    pq.put((heuristic(start, goal), start))
    visited = {start}
    
    while not pq.empty():
        _, current = pq.get()
        if current == goal: return True
        
        for neighbor in graph[current]:
            if neighbor not in visited:
                visited.add(neighbor)
                pq.put((heuristic(neighbor, goal), neighbor))`
    },
    "A*": {
        title: "A* Search",
        desc: "A* is an informed search algorithm, or a best-first search, meaning that it is formulated in terms of weighted graphs.",
        code: `def a_star(graph, start, goal):
    open_set = {start}
    came_from = {}
    
    g_score = {node: float('inf') for node in graph}
    g_score[start] = 0
    
    f_score = {node: float('inf') for node in graph}
    f_score[start] = heuristic(start, goal)
    
    while open_set:
        current = min(open_set, key=lambda n: f_score[n])
        if current == goal: return reconstruct_path(came_from, current)
        
        open_set.remove(current)
        for neighbor in graph[current]:
            tentative_g = g_score[current] + d(current, neighbor)
            if tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + h(neighbor, goal)
                open_set.add(neighbor)`
    }
};

const COLORS = {
    1: '#000000', // Wall
    2: '#ffffff', // Empty
    3: '#facc15', // Exploring (Yellow-400)
    4: '#ef4444', // Dead (Red-500)
    5: '#22c55e',  // Path (Green-500)
    10: '#3b82f6', // Start (Blue)
    11: '#ef4444'  // End (Red)
};

// Load Wall Texture
const wallImg = new Image();
wallImg.src = 'images/Minecraft-Stone-Bricks.jpg';
let wallImgLoaded = false;
wallImg.onload = () => {
    wallImgLoaded = true;
    if (currentMaze) drawMaze(); // Redraw if maze exists
};

const steveImg = new Image();
steveImg.src = 'images/Minecraft-Steve.jpeg';
let steveImgLoaded = false;
steveImg.onload = () => {
    steveImgLoaded = true;
    if (currentMaze) drawMaze();
};

const chestImg = new Image();
chestImg.src = 'images/Minecraft-Chest.jpeg';
let chestImgLoaded = false;
chestImg.onload = () => {
    chestImgLoaded = true;
    if (currentMaze) drawMaze();
};




const grassImg = new Image();
grassImg.src = 'images/Minecraft-Dirt-Path.webp';
let grassImgLoaded = false;
grassImg.onload = () => {
    grassImgLoaded = true;
    if (currentMaze) drawMaze();
};


const dirtImg = new Image();
dirtImg.src = 'images/Minecraft-Grass.png';
let dirtImgLoaded = false;
dirtImg.onload = () => {
    dirtImgLoaded = true;
    if (currentMaze) drawMaze();
};



const stoneImg = new Image();
stoneImg.src = 'images/Minecraft-Bricks.jpg';
let stoneImgLoaded = false;
stoneImg.onload = () => {
    stoneImgLoaded = true;
    if (currentMaze) drawMaze();
};



const pearlImg = new Image();
pearlImg.src = 'images/Minecraft-Ender-Pearl.png';
let pearlImgLoaded = false;
pearlImg.onload = () => {
    pearlImgLoaded = true;
    if (currentMaze) drawMaze();
};

let currentMaze = null;
let currentSteps = [];
let isRunning = false;
let playbackSpeed = 50;

// DOM Elements
const canvas = document.getElementById('mazeCanvas');
const ctx = canvas.getContext('2d');
const widthSlider = document.getElementById('width');
const heightSlider = document.getElementById('height');
const densitySlider = document.getElementById('density');
const btnGenerate = document.getElementById('btn-generate');
const btnRun = document.getElementById('btn-run');
const btnRunAll = document.getElementById('btn-run-all');
const algoSelect = document.getElementById('algorithm-select');
const speedSlider = document.getElementById('speed');

// Update UI Numbers
function updateLabels() {
    document.getElementById('val-width').innerText = widthSlider.value;
    document.getElementById('val-height').innerText = heightSlider.value;
    document.getElementById('val-density').innerText = densitySlider.value + '%';
    document.getElementById('val-speed').innerText = speedSlider.value < 33 ? 'Slow' : speedSlider.value < 66 ? 'Normal' : 'Fast';
}

[widthSlider, heightSlider, densitySlider, speedSlider].forEach(el => {
    el.addEventListener('input', updateLabels);
});

// Constraints Logic
const cbGuaranteed = document.getElementById('guaranteed_path');
const cbNoPath = document.getElementById('no_path');
const cbUnique = document.getElementById('unique_path');
const cbCycles = document.getElementById('allow_cycles');

cbGuaranteed.addEventListener('change', () => {
    if (cbGuaranteed.checked) cbNoPath.checked = false;
});
cbNoPath.addEventListener('change', () => {
    if (cbNoPath.checked) {
        cbGuaranteed.checked = false;
        cbUnique.checked = false;
    }
});
cbUnique.addEventListener('change', () => {
    if (cbUnique.checked) {
        cbGuaranteed.checked = true;
        cbNoPath.checked = false;
        cbCycles.checked = false;
        updateLabels();
    }
});
cbCycles.addEventListener('change', () => {
    if (cbCycles.checked) {
        cbUnique.checked = false;
    }
});

speedSlider.addEventListener('input', () => {
    playbackSpeed = parseInt(speedSlider.value);
});

algoSelect.addEventListener('change', updateAlgoInfo);

function updateAlgoInfo() {
    const key = algoSelect.value;
    const info = ALGO_INFO[key];
    if (info) {
        document.getElementById('algo-title').innerText = info.title;
        document.getElementById('algo-desc').innerText = info.desc;
    }
}

// Code Modal Logic (Wrapped for safety)
document.addEventListener('DOMContentLoaded', () => {
    const btnShowCode = document.getElementById('btn-show-code');
    const modalCode = document.getElementById('modal-code');
    const btnCloseCode = document.getElementById('btn-close-code');
    const codeContent = document.getElementById('code-content');
    const codeTitle = document.getElementById('code-title');
    const algoSelect = document.getElementById('algorithm-select');

    if (btnShowCode) {
        btnShowCode.addEventListener('click', (e) => {
            e.preventDefault();
            const key = algoSelect.value;
            const info = ALGO_INFO[key];
            if (info) {
                codeTitle.innerText = info.title + " Code";
                codeContent.innerText = info.code;
                modalCode.classList.remove('hidden');
            } else {
                console.error("Algorithm info not found for:", key);
            }
        });
    }

    if (btnCloseCode) btnCloseCode.addEventListener('click', () => modalCode.classList.add('hidden'));

    if (modalCode) {
        modalCode.addEventListener('click', (e) => {
            if (e.target === modalCode) modalCode.classList.add('hidden');
        });
    }
});

// Initial Update
updateAlgoInfo();

// Initialization
function resizeCanvas() {
    // Make canvas fit the container visually, but keep resolution
    const rect = canvas.parentElement.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height;
    drawMaze();
}

window.addEventListener('resize', resizeCanvas);

// Generate
async function generateMaze() {
    if (isRunning) return;

    const config = {
        width: parseInt(widthSlider.value),
        height: parseInt(heightSlider.value),
        wall_density: parseInt(densitySlider.value) / 100.0,
        start_fixed: true,
        end_fixed: true,
        guaranteed_path: document.getElementById('guaranteed_path').checked,
        no_path: document.getElementById('no_path').checked,
        unique_path: document.getElementById('unique_path').checked,
        allow_cycles: document.getElementById('allow_cycles').checked,
        dead_end_density: parseInt(document.getElementById('dead_end_density').value) / 100.0
    };

    try {
        const res = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });
        currentMaze = await res.json();
        drawMaze();
    } catch (e) {
        console.error("Failed to generate", e);
    }
}

btnGenerate.addEventListener('click', generateMaze);

// Drawing
function drawMaze(updates = null) {
    if (!currentMaze) return;

    const rows = currentMaze.height;
    const cols = currentMaze.width;

    // maintain aspect ratio
    const availW = canvas.width;
    const availH = canvas.height;

    const gridRatio = cols / rows;
    const canvasRatio = availW / availH;

    let drawW, drawH;

    // If model is wider than canvas relative to aspect -> Width constrained
    if (gridRatio > canvasRatio) {
        drawW = availW;
        drawH = drawW / gridRatio;
    } else {
        // Model is taller -> Height constrained
        drawH = availH;
        drawW = drawH * gridRatio;
    }

    const cellW = drawW / cols;
    const cellH = drawH / rows;

    const offX = (availW - drawW) / 2;
    const offY = (availH - drawH) / 2;

    if (!updates) {
        ctx.fillStyle = '#f3f4f6'; // Match bg-gray-100/200 approximately or white
        ctx.clearRect(0, 0, availW, availH);

        ctx.fillStyle = COLORS[1]; // default wall color for background of maze
        ctx.fillRect(offX, offY, drawW, drawH);

        for (let r = 0; r < rows; r++) {
            for (let c = 0; c < cols; c++) {
                const val = currentMaze.grid[r][c];
                const gap = cellW > 10 ? 1 : 0;
                const x = offX + c * cellW + gap / 2;
                const y = offY + r * cellH + gap / 2;
                const w = cellW - gap;
                const h = cellH - gap;

                if (val === 1 && wallImgLoaded) {
                    ctx.drawImage(wallImg, x, y, w, h);
                } else if (val === 2 && grassImgLoaded) {
                    ctx.drawImage(grassImg, x, y, w, h);
                } else if (val === 3 && pearlImgLoaded) {
                    ctx.drawImage(pearlImg, x, y, w, h);
                } else if (val === 4 && dirtImgLoaded) {
                    ctx.drawImage(dirtImg, x, y, w, h);
                } else if (val === 5 && stoneImgLoaded) {
                    ctx.drawImage(stoneImg, x, y, w, h);
                } else if (val === 10 && steveImgLoaded) {
                    ctx.drawImage(steveImg, x, y, w, h);
                } else if (val === 11 && chestImgLoaded) {
                    ctx.drawImage(chestImg, x, y, w, h);
                } else {
                    ctx.fillStyle = COLORS[val];
                    ctx.fillRect(x, y, w, h);
                }
            }
        }

        const start = currentMaze.start_pos;
        const end = currentMaze.end_pos;

        if (steveImgLoaded) {
            ctx.drawImage(steveImg, offX + start[1] * cellW, offY + start[0] * cellH, cellW, cellH);
        } else {
            ctx.fillStyle = 'blue';
            ctx.font = `${Math.max(10, cellH / 1.5)}px Arial`;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText("S", offX + start[1] * cellW + cellW / 2, offY + start[0] * cellH + cellH / 2);
        }

        if (chestImgLoaded) {
            ctx.drawImage(chestImg, offX + end[1] * cellW, offY + end[0] * cellH, cellW, cellH);
        } else {
            ctx.fillStyle = 'red';
            ctx.fillText("E", offX + end[1] * cellW + cellW / 2, offY + end[0] * cellH + cellH / 2);
        }

    } else {
        // Updates
        for (const [r, c, val] of updates) {
            const gap = cellW > 10 ? 1 : 0;
            const x = offX + c * cellW + gap / 2;
            const y = offY + r * cellH + gap / 2;
            const w = cellW - gap;
            const h = cellH - gap;

            if (val === 1 && wallImgLoaded) {
                ctx.drawImage(wallImg, x, y, w, h);
            } else if (val === 2 && grassImgLoaded) {
                ctx.drawImage(grassImg, x, y, w, h);
            } else if (val === 3 && pearlImgLoaded) {
                ctx.drawImage(pearlImg, x, y, w, h);
            } else if (val === 4 && dirtImgLoaded) {
                ctx.drawImage(dirtImg, x, y, w, h);
            } else if (val === 5 && stoneImgLoaded) {
                ctx.drawImage(stoneImg, x, y, w, h);
            } else if (val === 10 && steveImgLoaded) {
                ctx.drawImage(steveImg, x, y, w, h);
            } else if (val === 11 && chestImgLoaded) {
                ctx.drawImage(chestImg, x, y, w, h);
            } else {
                ctx.fillStyle = COLORS[val];
                ctx.fillRect(x, y, w, h);
            }

            // Keep Steve on top
            if (currentMaze && r === currentMaze.start_pos[0] && c === currentMaze.start_pos[1] && steveImgLoaded) {
                ctx.drawImage(steveImg, offX + c * cellW, offY + r * cellH, cellW, cellH);
            }

            // Keep Chest on top
            if (currentMaze && r === currentMaze.end_pos[0] && c === currentMaze.end_pos[1] && chestImgLoaded) {
                ctx.drawImage(chestImg, offX + c * cellW, offY + r * cellH, cellW, cellH);
            }
        }
    }
}

// Run Algorithm
async function runAlgorithm() {
    if (isRunning || !currentMaze) return;

    // Clear previous generic path (5) or dead (4) or exploring (3)
    // We must reset the maze to base state (1s and 2s only, plus Start/End)
    // Actually, backend generates fresh request for solve using currentMaze.
    // But frontend needs to visually clear.
    // We can just iterate grid and set 3,4,5 -> 2 ?
    // Or simpler: regenerate? No, we want same maze.
    // We'll iterate client side.
    for (let r = 0; r < currentMaze.height; r++) {
        for (let c = 0; c < currentMaze.width; c++) {
            if ([3, 4, 5].includes(currentMaze.grid[r][c])) {
                currentMaze.grid[r][c] = 2; // naive reset
            }
        }
    }

    // Restore Start/End values
    if (currentMaze) {
        currentMaze.grid[currentMaze.start_pos[0]][currentMaze.start_pos[1]] = 10;
        currentMaze.grid[currentMaze.end_pos[0]][currentMaze.end_pos[1]] = 11;
    }
    // Re-lock walls
    // (Walls are 1, they stay 1)

    // Update Start/End to 2 as well if they were overwritten?
    // Start is usually 2.
    drawMaze();

    const algo = algoSelect.value;
    isRunning = true;
    btnRun.disabled = true;
    btnGenerate.disabled = true;

    try {
        const res = await fetch('/api/solve', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                maze: currentMaze,
                algorithm: algo
            })
        });
        const steps = await res.json();

        let i = 0;

        function step() {
            if (!isRunning) return; // cancelled?

            // Speed logic: 
            // 1 = 1 step per 500ms?
            // 100 = 100 steps per frame??
            // Range 1-100.
            // Let's say:
            // High speed: execute multiple index increments per rAF.
            // Low speed: throttle rAF.

            const speedVal = parseInt(speedSlider.value);
            let stepsPerFrame = 1;
            let delay = 0;

            if (speedVal > 90) stepsPerFrame = 50;
            else if (speedVal > 70) stepsPerFrame = 10;
            else if (speedVal > 50) stepsPerFrame = 2;
            else {
                // Delay mode
                stepsPerFrame = 1;
                delay = (50 - speedVal) * 5; // max 250ms delay
            }

            // Execute batch
            for (let k = 0; k < stepsPerFrame; k++) {
                if (i >= steps.length) break;

                const s = steps[i];
                // Apply updates
                if (s.grid_updates) {
                    for (const [r, c, val] of s.grid_updates) {
                        currentMaze.grid[r][c] = val;
                    }
                    drawMaze(s.grid_updates); // optimize redraw
                }

                // Update stats
                if (i % 10 === 0 || i === steps.length - 1) { // throttle DOM updates
                    document.getElementById('res-nodes').innerText = s.nodes_expanded;
                    if (s.finished) {
                        document.getElementById('res-success').innerText = s.success ? "YES" : "NO";
                        if (s.success) document.getElementById('res-length').innerText = s.path_length;
                    }
                }
                i++;
            }

            if (i < steps.length) {
                if (delay > 0) setTimeout(() => requestAnimationFrame(step), delay);
                else requestAnimationFrame(step);
            } else {
                isRunning = false;
                btnRun.disabled = false;
                btnGenerate.disabled = false;
            }
        }

        step();

    } catch (e) {
        console.error("Solve error", e);
        isRunning = false;
        btnRun.disabled = false;
        btnGenerate.disabled = false;
    }
}

btnRun.addEventListener('click', runAlgorithm);


// Run All
const modal = document.getElementById('modal-run-all');
const tbody = document.getElementById('run-all-table-body');
document.getElementById('btn-close-modal').addEventListener('click', () => modal.classList.add('hidden'));

btnRunAll.addEventListener('click', async () => {
    if (isRunning || !currentMaze) return;

    tbody.innerHTML = '<tr><td colspan="5" class="text-center p-4">Running...</td></tr>';
    modal.classList.remove('hidden');

    // We can use the /batch endpoint but that generates NEW mazes.
    // Here we want to compare on THIS maze.
    // So we run sequentially.

    tbody.innerHTML = '';
    const algos = Object.keys(ALGO_INFO);

    for (const algo of algos) {
        const tr = document.createElement('tr');
        tr.className = "border-b";
        tr.innerHTML = `<td class="px-6 py-4 font-medium text-gray-900">${algo}</td>
                        <td class="px-6 py-4">...</td>
                        <td class="px-6 py-4">-</td>
                        <td class="px-6 py-4">-</td>
                        <td class="px-6 py-4">-</td>`;
        tbody.appendChild(tr);

        try {
            const res = await fetch('/api/solve', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ maze: currentMaze, algorithm: algo })
            });
            const steps = await res.json();
            const last = steps[steps.length - 1];

            tr.innerHTML = `<td class="px-6 py-4 font-medium text-gray-900">${algo}</td>
                            <td class="px-6 py-4 text-${last.success ? 'green' : 'red'}-600 font-bold">${last.success ? 'YES' : 'NO'}</td>
                            <td class="px-6 py-4">${last.path_length || '-'}</td>
                            <td class="px-6 py-4">${last.nodes_expanded}</td>
                            <td class="px-6 py-4">${steps.length}</td>`;

        } catch (e) {
            tr.innerHTML = `<td colspan="5" class="px-6 py-4 text-red-500">Error</td>`;
        }
    }
});

// Initial Load
resizeCanvas();
// Pre-populate with a maze
window.onload = generateMaze;

// Fullscreen Logic
document.addEventListener('DOMContentLoaded', () => {
    const btnFullscreen = document.getElementById('btn-fullscreen');
    const gridContainer = document.getElementById('grid-container');
    const btnRunFs = document.getElementById('btn-run-fs');
    const btnRun = document.getElementById('btn-run');

    // Wire up Run button in full screen
    if (btnRunFs && btnRun) {
        btnRunFs.addEventListener('click', (e) => {
            e.stopPropagation();
            btnRun.click();
        });
    }

    if (btnFullscreen && gridContainer) {
        btnFullscreen.addEventListener('click', () => {
            const isFull = gridContainer.classList.contains('fixed');
            if (isFull) {
                gridContainer.classList.remove('fixed', 'inset-4', 'z-50', 'shadow-2xl');
                gridContainer.classList.add('relative');
                btnFullscreen.innerText = "Fullscreen";
                if (btnRunFs) btnRunFs.classList.add('hidden');
            } else {
                gridContainer.classList.remove('relative');
                gridContainer.classList.add('fixed', 'inset-4', 'z-50', 'shadow-2xl');
                btnFullscreen.innerText = "Exit Fullscreen";
                if (btnRunFs) btnRunFs.classList.remove('hidden');
            }

            // Multiple resize calls to handle transition smoothly
            setTimeout(resizeCanvas, 50);
            setTimeout(resizeCanvas, 150);
            setTimeout(resizeCanvas, 310);
            resizeCanvas();
        });
    }
});
