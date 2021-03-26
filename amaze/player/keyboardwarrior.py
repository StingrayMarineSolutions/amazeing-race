import cv2
import numpy as np
from amaze.types import MazeImage, Position, Action


class KeyboardWarrior(object):
    def __init__(self):
        pass

    def forward(self, img: MazeImage, pos: Position) -> Action:
        key = cv2.waitKey(10) & 0xFF
        if key == ord('w'):
            return np.array([0, -5])
        elif key == ord('a'):
            return np.array([-5, 0])
        elif key == ord('d'):
            return np.array([5, 0])
        elif key == ord('s'):
            return np.array([0, 5])
        return np.array([0, 0])


class DummyPlayer(object):
    def __init__(self):
        pass

    def forward(self, img: MazeImage, pos: Position) -> Action:
        return np.array([0, 0])


class ActionRePlayer(object):
    def __init__(self, actions):
        self.actions = iter(actions)

    def forward(self, img: MazeImage, pos: Position) -> Action:
        action = next(self.actions)
        return np.array(action)