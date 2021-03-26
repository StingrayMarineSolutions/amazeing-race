import numpy as np
import random
from PIL import ImageDraw, Image
from collections import defaultdict
from typing import Tuple
import cv2
from amaze.maze.maze_util import int_divide_tuple, add_tuples, convert_tuple_to, scale_tuple, subtract_tuples

class Sector():
    def __init__(self, level, sector):
        self.neighbors = []
        self.level = level
        self.sector = sector
        self.visited = False

    def join(self, other):
        if self == other:
            return
        elif other in self.neighbors:
            return
        else:
            self.neighbors.append(other)
            other.neighbors.append(self)

    def center(self, r):
        arch = 2*np.pi / (2**(self.level+1))
        phi = (self.sector * 2 + 1) * arch
        r = (self.level + 0.5) * r
        return convert_tuple_to((np.sin(phi)*r, -np.cos(phi)*r), int)

    def __str__(self):
        return f'{self.level}-{self.sector}-{self.visited}'

    def __repr__(self):
        return str(self)

class CircularMaze():
    def __init__(self, seed: int = 42, size: Tuple[int, int] = (1024, 1024), num_levels: int = 7):
        self.size = size
        self.num_levels = num_levels
        self.seed = seed
        self.levels = defaultdict(list)

    def generate(self):
        random.seed(self.seed)

        # Build tree
        sectors = []
        # Inner level where louse is
        head = Sector(0, 0)
        self.levels[0].append(head)
        self.build_tree(head)

        # Join sector on same level
        for sectors in self.levels.values():
            for i, s in enumerate(sectors):
                s.join(sectors[i-1])

        mask = np.ones(self.size) * 255
        mask = Image.fromarray(mask)
        draw = ImageDraw.Draw(mask)
        center = int_divide_tuple(self.size, 2)
        ll = int_divide_tuple(center, self.num_levels+1)  # Size of each level
        thickness = 10

        # Draw all circles and sectors
        for i in range(self.num_levels+1):
            offset = scale_tuple(ll, i+1)
            tl = subtract_tuples(center, offset)
            br = add_tuples(center, offset)
            draw.ellipse([tl, br], outline='black', width=thickness)

            num_sectors = 2**i
            arch = 2 * np.pi / num_sectors
            if i == 0:  # Special case for inner level
                continue
            for s in range(num_sectors):
                s1 = i-0.05  # Small offset to make sure lines overlap
                s2 = i+1.00  # Small offset to make sure lines overlap
                phi = s * arch
                p1 = convert_tuple_to(add_tuples((np.sin(phi)*s1*ll[0], -np.cos(phi)*s1*ll[0]), center), int)
                p2 = convert_tuple_to(add_tuples((np.sin(phi)*s2*ll[0], -np.cos(phi)*s2*ll[0]), center), int)

                draw.line([p1, p2], fill='black', width=thickness)

        # Iterate and create actual mase
        paths = self.random_traversal(head)
        for p, travels in paths.items():
            for t in travels:
                if p.level == t.level:  # Open blocking wall
                    if abs(p.sector - t.sector) != 1:
                        s = 0
                    else:
                        s = max(p.sector, t.sector)
                    arch = 2 * np.pi / (2**p.level)
                    phi = s * arch
                    i = p.level * ll[0]+1
                    j = (p.level+1)*ll[0]-10
                    p1 = convert_tuple_to(add_tuples((np.sin(phi)*i, -np.cos(phi)*i), center), int)
                    p2 = convert_tuple_to(add_tuples((np.sin(phi)*j, -np.cos(phi)*j), center), int)
                    draw.line([p1, p2], fill='white', width=thickness+3)
                else:
                    l = max(p.level, t.level)
                    s = max(p.sector, t.sector)
                    tl = subtract_tuples(center, scale_tuple(ll, l+0.1))
                    br = add_tuples(center, scale_tuple(ll, l+0.1))
                    sArch = 360 * s / (2**l)-90
                    eArch = 360 * (s+1) / (2**l)-90
                    a = 90*thickness / (l * ll[0] * np.pi)
                    sArch += a
                    eArch -= a
                    draw.arc([tl, br], sArch, eArch, fill='white', width=thickness*3)

        mask = np.array(mask)

        self.img = np.expand_dims(mask, axis=-1).repeat(3, axis=-1).astype(np.uint8)
        self.mask = (255-mask).astype(np.uint8)
        pos = np.array(random.choice(self.levels[self.num_levels]).center(ll[0])) + np.array(center)
        return self.img, self.mask, pos, center

    def update(self):
        return self.img, self.mask


    def build_tree(self, head):
        if head.level == self.num_levels:
            return
        nl = head.level+1
        rc = Sector(nl, head.sector*2 + 0)
        lc = Sector(nl, head.sector*2 + 1)
        head.join(rc)
        head.join(lc)
        self.levels[nl].append(rc)
        self.levels[nl].append(lc)
        self.build_tree(rc)
        self.build_tree(lc)

    def random_traversal(self, head):
        paths = defaultdict(list)
        stack = [head]
        while stack:
            current = stack.pop()
            current.visited = True
            neighbors = [n for n in current.neighbors if not n.visited]
            if not neighbors:
                continue
            next = random.choice(neighbors)
            paths[current].append(next)
            stack.append(current)
            stack.append(next)
        return paths


