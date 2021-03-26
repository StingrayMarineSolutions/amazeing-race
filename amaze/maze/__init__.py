from .hexagonal_maze import HexagonalMaze
from .maze import SquareMaze
from .circular_maze import CircularMaze

mazes = {
    'HexagonalMaze': HexagonalMaze,
    'SquareMaze': SquareMaze,
    'CircularMaze': CircularMaze
}


def factory(maze, maze_args, **kwargs):
    mazetype = mazes.get(maze, None)
    if mazetype:
        return mazetype(**maze_args)
    raise Exception(f'No maze name {maze}')
