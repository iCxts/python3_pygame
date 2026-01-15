import time
import pygame
from pynput import keyboard
# pip install pynput

# =======================
# Keyboard
# =======================
class KBPoller:
    def __init__(self):
        self.pressed = set()
        listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release,
            suppress=True
        )
        listener.start()

    def on_press(self, key):
        try:
            self.pressed.add(key.char.lower())
        except AttributeError:
            pass

    def on_release(self, key):
        try:
            self.pressed.discard(key.char.lower())
        except AttributeError:
            pass


# =======================
# Player
# =======================
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def update(self, keys):
        if 'a' in keys:
            self.x -= 1
        if 'd' in keys:
            self.x += 1
        if 'w' in keys:
            self.y -= 1
        if 's' in keys:
            self.y += 1
        if 'q' in keys:
            return None


        self.x = max(0, min(100, self.x))
        self.y = max(0, min(100, self.y))


# =======================
# NPC (ไม่ใช้ dx dy)
# =======================
class NPC:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.dir_x = "right"   # left / right
        self.dir_y = "down"    # up / down

    def update(self):
        if self.dir_x == "right":
            self.x += 1
        else:
            self.x -= 1

        if self.dir_y == "down":
            self.y += 1
        else:
            self.y -= 1

        if self.x <= 0:
            self.x = 0
            self.dir_x = "right"
        elif self.x >= 100:
            self.x = 100
            self.dir_x = "left"

        if self.y <= 0:
            self.y = 0
            self.dir_y = "down"
        elif self.y >= 100:
            self.y = 100
            self.dir_y = "up"


# =======================
# Render
# =======================
def render(player, npc):
    print("player is at:", player.x, player.y)
    print("npc    is at:", npc.x, npc.y)
    print("----------------------")


# =======================
# Main loop
# =======================
kb = KBPoller()
player = Player(10, 10)
npc = NPC(50, 50)

running = True

while running:
    if 'q' in kb.pressed:
        running = False
        break

    player.update(kb.pressed)
    npc.update()
    render(player, npc)
    time.sleep(0.1)
