import json


n_actions = 1000
n_levels = 0
with open('resource/levels.txt', 'r') as f:
    for l in f:
        n_levels+=1

print(n_levels)

actions = [{'level': l, 'actions': [[0, 0] for _ in range(n_actions)]} for l in range(n_levels)]
print('Writing')
with open('resource/actions.json', 'w') as f:
    json.dump(actions, f)
