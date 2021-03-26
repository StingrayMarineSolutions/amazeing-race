from amaze.engine import Engine
from amaze.maze import factory as maze_factory
from amaze.player.keyboardwarrior import ActionRePlayer
from amaze.player.player import Player
import json
import argparse


class Evaluator():
    MAX_STEPS = 10000

    def __init__(self, visualize):
        self.visualize = visualize

    def evaluate_level(self, level, player, render=True):
        m = maze_factory(**level)
        e = Engine(m, visualize=self.visualize, consume_input=True, render=render)

        actions = []

        img, pos, status = e.forward(None)
        while status == 'RUNNING':
            try:
                action = player.forward(img, pos)
            except StopIteration:
                status = 'GAME OVER'
                break

            img, pos, status = e.forward(action)

            actions.append(action.tolist())

            if len(actions) >= self.MAX_STEPS:
                status = 'TIMEOUT'

        return status, actions

    def load_levels(self, filename):
        with open(filename) as f:
            data = f.read()
        return [json.loads(line) for line in data.strip().splitlines()]

    def load_actions_list(self, filename):
        with open(filename) as f:
            return json.load(f)

    def evaluate_levels(self, levels):
        return [self.evaluate_level(level, Player()) for level in levels]

    def compute_stats(self, results):
        nsuccess = sum(1 for (status, _) in results if status == 'YOU WON')
        total_actions = sum(len(actions) for (_, actions) in results)

        return {'num_success': nsuccess, 'total_actions': total_actions}

    def store_actions(self, results, filename):
        output = []
        for i, (_, actions) in enumerate(results):
            output.append({'level': i, 'actions': actions})

        with open(filename, 'w') as fp:
            json.dump(output, fp)

    def replay_levels(self, levels, actions_list):
        assert len(set((action['level'] for action in actions_list))) == len(actions_list), 'You can only play each level once'
        results = []

        for actions in actions_list:
            level = levels[actions['level']]
            p = ActionRePlayer(actions['actions'])
            results.append(self.evaluate_level(level, p, render=False))

        return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--actions', default=None)
    parser.add_argument('--levels', default='resource/levels.txt')
    parser.add_argument('--output', default=None)
    parser.add_argument('--visualize', action='store_true')
    args = parser.parse_args()

    ev = Evaluator(visualize=args.visualize)
    levels = ev.load_levels(args.levels)

    if args.actions:
        actions_list = ev.load_actions_list(args.actions)

        results = ev.replay_levels(levels, actions_list)
    else:
        results = ev.evaluate_levels(levels)

        if args.output:
            ev.store_actions(results, args.output)

    stats = ev.compute_stats(results)

    print(stats)
