from collections import namedtuple
from tqdm import tqdm

GameState = namedtuple("GameState", "player enemies score done")

SIZE = 32


def get_key(blocking=True):
    """get currently pressed key
    https://stackoverflow.com/a/13207724/9518712
    http://effbot.org/pyfaq/how-do-i-get-a-single-keypress-at-a-time.htm
    """
    import fcntl
    import os
    import select
    import sys
    import termios

    fd = sys.stdin.fileno()
    oldterm = termios.tcgetattr(fd)
    newattr = oldterm[:]
    newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
    # turns off stdin’s echoing and disables canonical mode
    termios.tcsetattr(fd, termios.TCSANOW, newattr)
    oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
    # obtain stdin’s file descriptor flags and modify them for non-blocking mode
    fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

    if blocking:
        # wait for incoming characters
        select.select([fd], [], [])
    key = sys.stdin.read(1)

    # close
    termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
    fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
    return key


def add_vectors(vec1, vec2):
    """saturating vector addition"""
    return tuple(max(min(i + j, SIZE - 1), 0) for i, j in zip(vec1, vec2))


def new_game():
    initial_pos = (SIZE // 2, SIZE // 2)
    enemies = []
    score = 0
    done = False
    return GameState(initial_pos, enemies, score, done)


def get_new_enemy_pos(player, enemy, score):
    vector = [(i > j) - (i < j) for i, j in zip(player, enemy)]

    if all(vector):
        vector[score % 2] = 0
    return add_vectors(enemy, vector)


def update(game, direction):
    score = game.score + 1
    move_vector = {"UP": (0, -1), "DOWN": (0, 1), "LEFT": (-1, 0), "RIGHT": (1, 0)}
    player = add_vectors(game.player, move_vector[direction])

    if score % 3:
        new_enemy = []
    else:
        new_enemy = [[(0, 0), (31, 31), (31, 0), (0, 31)][score % 4]]

    done = False
    enemies = []
    for enemy in game.enemies + new_enemy:
        new_pos = get_new_enemy_pos(player, enemy, score)
        enemies.append(new_pos if all(other != new_pos for other in enemies) else enemy)
        if enemies[-1] == player:
            done = True
            break
    return GameState(player, enemies, score, done)


def print_game(game):
    board = [[" "] * SIZE for _ in range(SIZE)]
    for x, y in game.enemies:
        board[y][x] = "X"
    x, y = game.player
    board[y][x] = "O"
    out = "\n".join(f"|{'|'.join(row)}|" for row in board)
    print(out)


def solve(n=10000, best=None, state=None):
    """depth first search
    keep track of longest path
    """
    if state:
        games, path = state
    else:
        games = [(None, new_game())]
        path = []

    if best:
        best_game, best_path = best
    else:
        best_game = games[-1][1]
        best_path = []

    for _ in tqdm(range(n)):
        move, game = games.pop()  # get best path so far

        if move:
            if len(path) + 1 > game.score:
                moves_to_delete = len(path) + 1 - game.score
                del path[-moves_to_delete:]  # remove dead paths
            path.append(move)

        if game.done:
            if game.score > best_game.score:
                best_game = game
                best_path = list(path)
            continue

        for move in ("DOWN", "RIGHT", "UP", "LEFT"):
            games.append((move, update(game, move)))

    return (best_game, best_path), (games, path)


def test():
    best, state = solve(1000)
    game, path = best
    print("longest path:", len(path))
    print("paths remaining:", len(state[0]))
    print(path)


def play():
    game = new_game()
    while not game.done:
        print_game(game)
        print(game.score)
        key = get_key()
        direction = {"l": "UP", "n": "DOWN", "r": "LEFT", "s": "RIGHT"}[key]
        game = update(game, direction)
    print_game(game)
    print("game over:", game.score)


if __name__ == "__main__":
    play()
