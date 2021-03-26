#based on: 
# http://sites.nd.edu/code-fair/2018/11/07/maze-generation-advanced/

import numpy
from numpy.random import random_integers as rand
import matplotlib.pyplot as plot
import random

WALL = 1
PATH = 0

def convert_tuple_to(t1, type):
    return tuple([type(t) for t in t1])

def add_tuples(t1, t2):
    return tuple([t1[i] + t2[i] for i in range(len(t1))])

def subtract_tuples(t1, t2):
    return tuple([t1[i] - t2[i] for i in range(len(t1))])

def multiply_tuples(t1, t2):
    return tuple([t1[i] * t2[i] for i in range(len(t1))])

def divide_tuples(t1, t2):
    return tuple([t1[i] / t2[i] for i in range(len(t1))])

def int_divide_tuple(t1, divisor):
    return tuple([t1[i] // divisor for i in range(len(t1))])

def scale_tuple(t1, s):
    return tuple([t1[i] * s for i in range(len(t1))])

def int_divide_tuples(t1, t2):
    return tuple([t1[i] // t2[i] for i in range(len(t1))])

def is_in_bounds(point, dimensions):
    return (point[0] > 0) and (point[0] < dimensions[0]) and (point[1] > 0) and (point[1] < dimensions[1])

def get_neighbors(point, maze):
    directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
    neighbors = [add_tuples(point, d) for d in directions if is_in_bounds(add_tuples(point, d), maze.shape)]
    return neighbors

def get_connected_neighors(point, maze):
    directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
    neighbors = [add_tuples(point, d) for d in directions if is_in_bounds(add_tuples(point, d), maze.shape) and maze[add_tuples(point, int_divide_tuples(d, (2, 2)))] == PATH]
    return neighbors

def get_unconnected_neighbors(point, maze):
    directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
    neighbors = [add_tuples(point, d) for d in directions if is_in_bounds(add_tuples(point, d), maze.shape) and maze[add_tuples(point, int_divide_tuples(d, (2, 2)))] == WALL]
    return neighbors

def generate_maze(dimensions):
     # Since walls are 1 thick and paths are 1 thick
    # and there are walls on the far and near side,
    # the dimensions of the maze must be odd
    dimensions = add_tuples(multiply_tuples(int_divide_tuples(dimensions, (2, 2)), (2, 2)), (1, 1))

    # Make the rectangular array that will represent
    # the maze as of either zeros (path) or ones (walls)
    # Start with no walls
    maze = numpy.zeros(dimensions, dtype=bool)

    # Make walls around the outside
    for y in range(0, dimensions[0], 2): maze[y, :] = WALL;
    for x in range(0, dimensions[1], 2): maze[:, x] = WALL

    startPosition = (0, 1)
    endPosition = (-1, -2)
    
    maze[startPosition] = 0
    maze[endPosition] = 0

    stack = [(1, 1)]

    while len(stack) > 0:
        if(rand(2) == 1): 
            currentPosition = stack.pop()
        else: 
            index = rand(len(stack)) - 1
            currentPosition = stack[index]
            del(stack[index])

        unvisitedNeighbors = [neighbor for neighbor in get_unconnected_neighbors(currentPosition, maze) if len(get_connected_neighors(neighbor, maze)) == 0]

        if len(unvisitedNeighbors) > 0:
           random.shuffle(unvisitedNeighbors)
           nextPosition = unvisitedNeighbors.pop();

           if len(unvisitedNeighbors) > 0: stack.append(currentPosition)

           direction = subtract_tuples(nextPosition, currentPosition);
           halfDirection = int_divide_tuples(direction, (2, 2));

           for step in range(rand(3, 5)):
               maze[add_tuples(currentPosition, halfDirection)] = PATH

               currentPosition = nextPosition
               nextPosition = add_tuples(currentPosition, direction)

               stack.append(currentPosition)
               if not is_in_bounds(nextPosition, dimensions) or len(get_connected_neighors(nextPosition, maze)) > 0:
                   break;

    return maze

def generate_maze_image(maze, solution):
    dimensions = maze.shape
    image = numpy.zeros(dimensions, dtype=float)
    image[:, :] = 0.0
    for x in range(maze.shape[0]):
        for y in range(maze.shape[1]):
            if maze[x, y] == WALL:
                image[x, y] = 0.0
            else: 
                image[x, y] = 1.0
    for point in solution:
        if point[0] < 0 or point[1] < 0 or point[0] >= dimensions[0] or point[1] >= dimensions[1]:
           continue;
        if maze[point[1], point[0]] == WALL:
            image[point[1], point[0]] = 0.5
        else:
            image[point[1], point[0]] = 0.85
    return image

def show_maze(maze):
    image = generate_maze_image(maze, []);
    plot.imshow(image, cmap=plot.cm.gist_heat)
    plot.xticks([])
    plot.yticks([])
    plot.show()

def show_maze_and_solution(maze, solution):
    image = generate_maze_image(maze, solution)
    plot.imshow(image, cmap=plot.cm.gist_heat)
    plot.xticks([])
    plot.yticks([])
    plot.show()