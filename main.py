import pygame
import math
import random
from queue import PriorityQueue

# Initialize Pygame
pygame.init()

# ~~~~~~~~~~~~~~~~~~ UI THEME ~~~~~~~~~~~~~~~~~~
LINE_TINT = (45, 45, 45)         
BG_COLOR = (25, 25, 25)          # GREY elephant
START_COLOR = (46, 204, 113)     # GREEN parrot 
END_COLOR = (231, 76, 60)        # RED panda
WALL_COLOR = (200, 200, 200)     # WHITE swan
OPEN_COLOR = (52, 152, 219)      # BLUE peacock
CLOSED_COLOR = (102, 0, 153)     # PURPLE sea star
PATH_COLOR = (241, 196, 15)      # YELLOW caiman

class Tile:
    """Represents a single cell in the grid"""
    def __init__(self, row, col, size, grid_size):
        self.row = row
        self.col = col
        self.x = row * size
        self.y = col * size
        self.color = BG_COLOR
        self.size = size
        self.grid_size = grid_size

    def get_coords(self): return self.row, self.col
    
    # State checks
    def is_closed(self): return self.color == CLOSED_COLOR
    def is_open(self): return self.color == OPEN_COLOR
    def is_wall(self): return self.color == WALL_COLOR
    def is_start(self): return self.color == START_COLOR
    def is_end(self): return self.color == END_COLOR

    # State mutations
    def reset(self): self.color = BG_COLOR
    def make_start(self): self.color = START_COLOR
    def make_closed(self): self.color = CLOSED_COLOR
    def make_open(self): self.color = OPEN_COLOR
    def make_wall(self): self.color = WALL_COLOR
    def make_end(self): self.color = END_COLOR
    def make_path(self): self.color = PATH_COLOR

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.size, self.size))

    def fetch_adjacent(self, grid, diagonal=True):
        """Finds valid neighbors"""
        self.neighbors = []
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)] 
        if diagonal:
            directions += [(1, 1), (-1, -1), (1, -1), (-1, 1)] 
        
        for dr, dc in directions:
            r, c = self.row + dr, self.col + dc
            if 0 <= r < self.grid_size and 0 <= c < self.grid_size:
                if not grid[r][c].is_wall():
                    self.neighbors.append(grid[r][c])


class AlgorithmVisualizer:
    def __init__(self, width=800, rows=51):
        self.width = width
        self.rows = rows
        self.window = pygame.display.set_mode((width, width))
        pygame.display.set_caption("A* Pathfinding Analyzer & Maze Generator")
        self.grid = self._init_grid()

    def _init_grid(self):
        size = self.width // self.rows
        return [[Tile(i, j, size, self.rows) for j in range(self.rows)] for i in range(self.rows)]

    def _draw_mesh(self):
        size = self.width // self.rows
        for i in range(self.rows):
            pygame.draw.line(self.window, LINE_TINT, (0, i * size), (self.width, i * size))
            for j in range(self.rows):
                pygame.draw.line(self.window, LINE_TINT, (j * size, 0), (j * size, self.width))

    def _update_display(self):
        self.window.fill(BG_COLOR)
        for row in self.grid:
            for tile in row:
                tile.draw(self.window)
        self._draw_mesh()
        pygame.display.update()

    def _get_mouse_tile(self, pos):
        size = self.width // self.rows
        y, x = pos
        return self.grid[y // size][x // size]

    @staticmethod
    def get_distance(p1, p2):
        x1, y1 = p1
        x2, y2 = p2
        return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

    def _trace_route(self, parent_map, curr_tile):
        while curr_tile in parent_map:
            curr_tile = parent_map[curr_tile]
            if not curr_tile.is_start():
                curr_tile.make_path()
            self._update_display()

    def _execute_search(self, start, end):
        step_counter = 0
        search_queue = PriorityQueue()
        search_queue.put((0, step_counter, start))
        parent_map = {}
        
        cost_from_start = {tile: float("inf") for row in self.grid for tile in row}
        cost_from_start[start] = 0
        
        estimated_total_cost = {tile: float("inf") for row in self.grid for tile in row}
        estimated_total_cost[start] = self.get_distance(start.get_coords(), end.get_coords())

        in_queue_tracker = {start}

        while not search_queue.empty():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

            curr_tile = search_queue.get()[2]
            in_queue_tracker.remove(curr_tile)

            if curr_tile == end:
                self._trace_route(parent_map, end)
                end.make_end()
                return True

            for adj in curr_tile.neighbors:
                step_cost = 1.414 if abs(curr_tile.row - adj.row) == 1 and abs(curr_tile.col - adj.col) == 1 else 1
                tentative_cost = cost_from_start[curr_tile] + step_cost

                if tentative_cost < cost_from_start[adj]:
                    parent_map[adj] = curr_tile
                    cost_from_start[adj] = tentative_cost
                    estimated_total_cost[adj] = tentative_cost + self.get_distance(adj.get_coords(), end.get_coords())
                    
                    if adj not in in_queue_tracker:
                        step_counter += 1
                        search_queue.put((estimated_total_cost[adj], step_counter, adj))
                        in_queue_tracker.add(adj)
                        if adj != end:
                            adj.make_open()

            self._update_display()

            if curr_tile != start:
                curr_tile.make_closed()

        return False

    def build_labyrinth(self):
        """Generates a perfect maze using Recursive Backtracking"""
        # Step 1: Fill entire grid with walls
        for row in self.grid:
            for tile in row:
                tile.make_wall()
        
        def fetch_unvisited_adjacent(r, c):
            valid_adj = []
            directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if 0 < nr < self.rows - 1 and 0 < nc < self.rows - 1:
                    if self.grid[nr][nc].is_wall():
                        valid_adj.append((nr, nc))
            return valid_adj

        # Step 2: Initialize stack and starting point
        start_r, start_c = 1, 1
        self.grid[start_r][start_c].reset() 
        dfs_stack = [(start_r, start_c)]

        # Step 3: DFS Carving loop
        while dfs_stack:
            curr_r, curr_c = dfs_stack[-1]
            valid_adj = fetch_unvisited_adjacent(curr_r, curr_c)

            if valid_adj:
                next_r, next_c = random.choice(valid_adj)
                
                wall_r = curr_r + (next_r - curr_r) // 2
                wall_c = curr_c + (next_c - curr_c) // 2
                
                self.grid[wall_r][wall_c].reset() 
                self.grid[next_r][next_c].reset() 
                
                dfs_stack.append((next_r, next_c))
            else:
                dfs_stack.pop()
        
        self._update_display()

    def reset_search_state(self, start, end):
        """Clears the search history but keeps the walls"""
        for row in self.grid:
            for tile in row:
                if tile.is_open() or tile.is_closed() or tile.color == PATH_COLOR:
                    tile.reset()
        if start: start.make_start()
        if end: end.make_end()

    def run(self):
        start_point = None
        end_point = None
        is_running = True

        while is_running:
            self._update_display()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    is_running = False

                # Left Click - Draw
                if pygame.mouse.get_pressed()[0]:
                    tile = self._get_mouse_tile(pygame.mouse.get_pos())
                    if not start_point and tile != end_point:
                        start_point = tile
                        start_point.make_start()
                    elif not end_point and tile != start_point:
                        end_point = tile
                        end_point.make_end()
                    elif tile != end_point and tile != start_point:
                        tile.make_wall()

                # Right Click - Erase
                elif pygame.mouse.get_pressed()[2]:
                    tile = self._get_mouse_tile(pygame.mouse.get_pos())
                    tile.reset()
                    if tile == start_point: start_point = None
                    elif tile == end_point: end_point = None

                if event.type == pygame.KEYDOWN:
                    # Execute Search
                    if event.key == pygame.K_SPACE and start_point and end_point:
                        for row in self.grid:
                            for tile in row:
                                tile.fetch_adjacent(self.grid, diagonal=True)
                        self._execute_search(start_point, end_point)

                    # Hard Reset
                    if event.key == pygame.K_c:
                        start_point = None
                        end_point = None
                        self.grid = self._init_grid()
                    
                    # Soft Reset
                    if event.key == pygame.K_r:
                        self.reset_search_state(start_point, end_point)

                    # Generate Maze
                    if event.key == pygame.K_m:
                        start_point = None
                        end_point = None
                        self.build_labyrinth()

        pygame.quit()


if __name__ == "__main__":
    app = AlgorithmVisualizer(rows=51)
    app.run()