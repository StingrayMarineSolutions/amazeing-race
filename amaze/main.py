'''
This is a sample of how to use amaze framework.
'''
import argparse
import json
import engine
from maze import factory as maze_factory
from amaze.player.keyboardwarrior import KeyboardWarrior

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--level', type=int, default=0)
args = parser.parse_args()

with open('resource/levels.txt') as f:
    levels = [json.loads(line) for line in f]

p = KeyboardWarrior()
m = maze_factory(**levels[args.level])
e = engine.Engine(m)

g = engine.Game(engine=e, player=p)
g.run()