import time
from pynput import keyboard
# pip install pynput

class KBPoller:
    def on_press(self, key):
        try:
            ch = key.char.lower()
            self.pressed.add(ch)
        except AttributeError:
            pass

    def on_release(self, key):
        try:
            ch = key.char.lower()
            self.pressed.remove(ch)
        except AttributeError:
            pass

    def __init__(self):
        self.pressed = set()

        listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release,suppress=True)
        listener.start()


kb = KBPoller()

running = True

player_x = 10
player_y = 10

npc_x = 50
npc_y = 50
npc_x_move = 1 
npc_y_move = 2

x_min = 0
x_max = 100
y_min = 0
y_max = 100

def scan_keys(kb):
    if 'a' in kb.pressed:
        return 'a'
    elif 'd' in kb.pressed:
        return 'd'
    elif 'w' in kb.pressed:
        return 'w'
    elif 's' in kb.pressed:
        return 's'
    elif 'q' in kb.pressed:
        return 'q'
    else:
        return None


def render_state():
    print("player is at:", player_x, player_y)
    print("npc is at:", npc_x, npc_y)
def update_state(inp):
    global player_x, player_y, running, npc_x, npc_y, npc_y_move, npc_x_move
    

    npc_x += npc_x_move
    npc_y_move += npc_y_move

    if inp == "a":
        player_x -= 1
    elif inp == "d":
        player_x += 1
    elif inp == "w":
        player_y -= 1
    elif inp == "s":
        player_y += 1
    elif inp == "q":
        running = False

    if player_x < x_min:
        player_x = x_min
    if player_x > x_max:
        player_x = x_max
    if player_y < y_min:
        player_y = y_min
    if player_y > y_max:
        player_y = y_max

    if npc_x <= x_min:
        npc_x_move = npc_x_move * -1 
    if npc_x >= x_max:
        npc_x_move = npc_x_move * -1 
    if npc_y <= y_min:
        npc_y_move = npc_y_move * -1
    if npc_y >= y_max:
        npc_y_move = npc_y_move * -1


while running:

    # read/check for user actions (input)
    # update game state (physics, AI, etc)
    # render game state (graphics)
    inp = scan_keys(kb)
    if inp is not None:
        update_state(inp)
    render_state()

    time.sleep(0.1)

