"""square game"""
from collections import namedtuple

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


State = namedtuple("State", "player enemies score done")


def new_game():
    """make a new game"""
    return State((SIZE // 2, SIZE // 2), [], 0, False)


def next_state(state: State, action: str):
    """this function is gross because it needs to be fast"""
    score = state.score + 1
    move = {"UP": (0, -1), "DOWN": (0, 1), "LEFT": (-1, 0), "RIGHT": (1, 0)}[action]
    # update player position with saturating vector addition
    player = tuple(max(min(i + j, SIZE - 1), 0) for i, j in zip(state.player, move))

    # copy enemies
    enemies = state.enemies[:]
    if score % 3 == 0:
        enemies.append(((0, 0), (31, 31), (31, 0), (0, 31))[score % 4])

    seen = set(enemies)

    # update enemy positions
    done = False
    for i, enemy in enumerate(enemies):

        # ====get new player pos====
        if player[0] > enemy[0]:
            dx = 1
        elif player[0] < enemy[0]:
            dx = -1
        else:
            dx = 0

        if player[1] > enemy[1]:
            dy = 1
        elif player[1] < enemy[1]:
            dy = -1
        else:
            dy = 0

        if dx and dy:
            if score % 2:
                dy = 0
            else:
                dx = 0
        new_pos = enemy[0] + dx, enemy[1] + dy
        # ==========================

        if new_pos not in seen:  # don't move enemy if they collide
            seen.remove(enemy)
            seen.add(new_pos)
            enemies[i] = new_pos

        if player == enemies[i]:
            done = True
            break

    return State(player, enemies, score, done)


def get_board_str(state: State):
    """print the board"""
    grid = [[" "] * SIZE for _ in range(SIZE)]
    for x, y in state.enemies:
        grid[y][x] = "X"
    x, y = state.player
    grid[y][x] = "O"
    out = "\n".join(f"|{'|'.join(row)}|" for row in grid)
    return out


def play():
    """play game interactively"""
    path = []
    state = new_game()
    while not state.done:
        print(get_board_str(state))
        print(state.score)
        key = get_key()
        action = {"l": "UP", "n": "DOWN", "r": "LEFT", "s": "RIGHT"}[key]
        # action = {"w": "UP", "s": "DOWN", "a": "LEFT", "d": "RIGHT"}[key]
        state = next_state(state, action)
        path.append(action)
    print(get_board_str(state))
    print("game over:", state.score)
    print(get_compact_path(path))


def get_compact_path(path):
    string = ""
    for i, move in enumerate(path, 1):
        if i == len(path) or move != path[i]:
            string += f"{move.lower()} {i}, "
    return string


if __name__ == "__main__":
    play()

