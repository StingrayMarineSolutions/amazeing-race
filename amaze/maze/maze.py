import cv2
import numpy as np
from .maze_util import generate_maze, generate_maze_image
import random
from typing import List, Tuple
from amaze.types import MazeImage, MazeMask, StartPos, GoalPos


class SquareMaze(object):
    def __init__(self, size: Tuple[int, int] = (1025, 1025), seed: int = 1235):
        self.mask = None
        self.img = None
        self.startpos = None
        self.goal = None
        self.size = size
        self.seed = seed

    def generate(self) -> Tuple[MazeImage, MazeMask, StartPos, GoalPos]:
        random.seed(self.seed)
        np.random.seed(self.seed)
        scale = 32
        dimensions = [self.size[0]//scale, self.size[1]//scale]
        maze = generate_maze(dimensions)
        mazeImg = generate_maze_image(maze, []) * 255.0

        self.img = np.expand_dims(np.kron(mazeImg, np.ones((scale, scale))), axis=2).repeat(3, axis=2).astype(np.uint8)
        self.mask = np.kron(maze, np.ones((scale, scale))).astype(np.uint8)

        off = (scale * 3) // 2
        return self.img, self.mask, np.array([45, 20]), np.array([self.img.shape[1]-off, self.img.shape[0]-scale])

    def update(self) -> Tuple[MazeImage, MazeMask]:
        return self.img, self.mask
