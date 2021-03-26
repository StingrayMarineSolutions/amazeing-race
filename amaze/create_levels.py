import json
import random
import numpy as np

num_square_levels = 30
num_hex_levels = 30
num_circ_levels = 30

def seed_generator(N):
    used = set()
    while len(used) < N:
        s = random.randint(0, 32000000)
        used.add(s)
        yield s

with open('resource/levels.txt', 'w') as f:
    for i in seed_generator(num_square_levels):
        level = {"maze": "SquareMaze", "maze_args": {"size": [1024, 1024], "seed": i}}
        f.write(json.dumps(level))
        f.write('\n')
    for i in seed_generator(num_hex_levels):
        level = {"maze": "HexagonalMaze", "maze_args": {"size": [1024, 1024], "seed": i, 'num_cells': 10}}
        f.write(json.dumps(level))
        f.write('\n')
    for i in seed_generator(num_square_levels):
        level = {"maze": "CircularMaze", "maze_args": {"size": [1024, 1024], "seed": i, 'num_levels': 7}}
        f.write(json.dumps(level))
        f.write('\n')
