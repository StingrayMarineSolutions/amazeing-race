import cv2
import random
import numpy as np
from collections import defaultdict
from typing import List, Dict, Tuple


class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.visited = False
        self.pos_x = x
        if x % 2:
            self.pos_y = y + 1 / 3
        else:
            self.pos_y = y


Cells = List[List[Cell]]
Paths = Dict[Cell, List[Cell]]

MazeImage = np.array
MazeMask = np.array
StartPos = np.array
GoalPos = np.array


class HexagonalMaze:
    def __init__(self, size: Tuple[int, int] = (1024, 1024), num_cells: int = 10, seed: int = 42):
        self.size = size
        self.num_cells = num_cells
        self.size_x = num_cells
        self.size_y = num_cells
        self.img = None
        self.mask = None
        self.seed = seed

    def generate(self) -> Tuple[MazeImage, MazeMask, StartPos, GoalPos]:
        random.seed(self.seed)
        cells = [[Cell(x, y) for x in range(self.size_x)]
                 for y in range(self.size_y)]
        paths = self.random_traversal(cells)
        img = self.render(cells, paths)
        self.mask = 255 - img.copy()
        self.img = np.expand_dims(img, -1).repeat(3, axis=-1)
        startpos, goalpos = self.get_start_goal(cells)
        return self.img, self.mask, startpos, goalpos

    def update(self) -> Tuple[MazeImage, MazeMask]:
        return self.img, self.mask

    def random_traversal(self, cells: Cells) -> Paths:
        paths = defaultdict(list)
        stack = [cells[0][0]]
        while stack:
            current = stack.pop()
            current.visited = True
            neighbors = [n for n in self.get_neighbors(current, cells) if not n.visited]
            if not neighbors:
                continue
            next = random.choice(neighbors)
            paths[current].append(next)
            stack.append(current)
            stack.append(next)
        return paths

    def get_neighbors(self, cell: Cell, cells: Cells) -> List[Cell]:
        neighbors = []
        x, y = cell.x, cell.y
        if y > 0:
            neighbors.append(cells[y-1][x])  # top
        if y < self.size_y - 1:
            neighbors.append(cells[y+1][x])  # bottom
        if x % 2:  # odd
            neighbors.append(cells[y][x-1])  # top left
            if y < self.size_y - 1:
                neighbors.append(cells[y+1][x-1])  # bottom left
            if x < self.size_x - 1:
                neighbors.append(cells[y][x+1])  # top right
                if y < self.size_y - 1:
                    neighbors.append(cells[y+1][x+1])  # bottom right
        else:  # even
            if x > 0:
                neighbors.append(cells[y][x-1])  # bottom left
                if y > 0:
                    neighbors.append(cells[y-1][x-1])  # top left
            if x < self.size_x - 1:
                neighbors.append(cells[y][x+1]) # bottom right
                if y > 0:
                    neighbors.append(cells[y-1][x+1])  # top right
        return neighbors

    def get_render_sizes(self) -> Tuple[int, int]:
        cell_size = self.size[0] // self.size_x
        path_size = int(cell_size * 0.4)
        return cell_size, path_size

    def render(self, cells: Cells, paths: Paths) -> MazeImage:
        path_color = (255, 255, 255)
        image_size = self.size[0], self.size[1]
        img = np.zeros(shape=image_size, dtype=np.uint8)
        cell_size, path_size = self.get_render_sizes()
        for y in range(self.size_y):
            for x in range(self.size_x):
                curr = cells[y][x]
                neighbors = paths[curr]
                start = np.array([curr.pos_x, curr.pos_y]) * cell_size + path_size
                for n in neighbors:
                    end = np.array([n.pos_x, n.pos_y]) * cell_size + path_size
                    cv2.line(img, tuple(start.astype(np.int32)), tuple(end.astype(np.int32)), path_color, path_size)
        return img

    def get_start_goal(self, cells: Cells) -> Tuple[StartPos, GoalPos]:
        cell_size, path_size = self.get_render_sizes()
        flat = [cell for row in cells for cell in row]
        start_cell = random.choice(flat)
        end_cell = random.choice(flat)
        while start_cell == end_cell:
            end_cell = random.choice(flat)
        startpos = np.array([start_cell.pos_x, start_cell.pos_y]) * cell_size + path_size
        goalpos = np.array([end_cell.pos_x, end_cell.pos_y]) * cell_size + path_size
        return startpos.astype(np.int32), goalpos.astype(np.int32)

