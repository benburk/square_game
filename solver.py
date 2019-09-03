from main import *
import cProfile
from tqdm import tqdm


def solve(n=1000, best_path=None, internal=None):
    if internal:
        states, legal_moves, path = internal
    else:
        states = [new_game()]
        legal_moves = []
        path = []
    
    if best_path:
        best_path = best_path
    else:
        best_path = states[-1]

    for i in tqdm(range(n)):
        state = states[-1]  # get current state

        if len(path) > len(best_path):  # longest path?
            best_path = path[:]

        if state.done:  # backtrack
            path.pop()
            states.pop()
            while not legal_moves[-1]:
                legal_moves.pop()
                path.pop()
                states.pop()
        else:
            legal_moves.append(["DOWN", "RIGHT", "UP", "LEFT"])

        action = legal_moves[-1].pop()
        path.append(action)
        states.append(next_state(states[-1], action))

    return best_path, (states, legal_moves, path)

def test():
    import pickle

    internal = pickle.load(open("internal.pickle", "rb"))
    print(len(internal[0]))



if __name__ == "__main__":
    # search(new_game())
    # play()
    # solve2()
    test()
    # cProfile.run("solve()", sort=2)
