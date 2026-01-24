import math
import time
import random

from bullet import Bullet
from characters import NPC


def colliderect(rect1, rect2):
    return rect1[0] < rect2[2] and rect1[2] > rect2[0] and rect1[1] < rect2[3] and rect1[3] > rect2[1]

class GameEngine:
    def __init__(self, graph_engine, input_controller, game_field, player, npcs, *, fps=60):

        self.graph_engine = graph_engine

        self.game_field = game_field
        self.player = player
        self.npcs = npcs
        self.fps = fps
        self.bullets = []

        self.input_controller = input_controller

    def collide(self):
        for idx, npc in enumerate(self.npcs):
            if colliderect(self.player.get_bounding_box(), npc.get_bounding_box()):
                return idx
        return None

    def update_state(self, pressed_keys, mouse_click_pos):
        if mouse_click_pos is not None:
            # self.player.x, self.player.y = mouse_click_pos
            self.npcs.append(NPC(mouse_click_pos[0], mouse_click_pos[1], random.randint(-2, 2), random.randint(-2, 2)))

        for npc in self.npcs:
            npc.move(self.game_field)

        for bullet in self.bullets:
            bullet.move(self.game_field)
            if (bullet.y > self.game_field.y_max or bullet.y < self.game_field.y_min
                    or bullet.x > self.game_field.x_max or bullet.x < self.game_field.x_min):
                self.bullets.remove(bullet)

        self.player.move("a" in pressed_keys, "d" in pressed_keys, "w" in pressed_keys, "s" in pressed_keys, "z" in pressed_keys, self.game_field)

        if " " in pressed_keys:
            b = Bullet(self.player.x, self.player.y, math.cos(math.radians(self.player.angle)),
                       math.sin(math.radians(self.player.angle)))
            self.bullets.append(b)

        collided_with_player = self.collide()
        if collided_with_player is not None:
            print("Collision with player!")
            del self.npcs[collided_with_player]

        if "q" in pressed_keys:
            self.running = False

    def render_state(self):
        self.graph_engine.start_frame()

        self.graph_engine.render_circle(self.player.x, self.player.y, 20, "red")

        x1 = self.player.x
        y1 = self.player.y
        x2 = self.player.x + 20 * math.cos(math.radians(self.player.angle))
        y2 = self.player.y + 20 * math.sin(math.radians(self.player.angle))

        self.graph_engine.render_line(x1, y1, x2, y2, "black")

        # x1,y1 to x2,y1 - angle zero
        # x1,y1 to x1,y2 - angle 90
        # for arbitrary angle, use trigonometry


        for npc in self.npcs:
            self.graph_engine.render_circle(npc.x, npc.y, 20, "blue")

        for bullet in self.bullets:
            self.graph_engine.render_rectangle(bullet.x - 2, bullet.y - 2, 4, 4, "red")

        self.graph_engine.show_frame()

    def run_game(self):
        self.running = True
        while self.running:
            self.render_state()

            pressed_keys = self.input_controller.get_pressed_keys()
            mouse_click_pos = self.input_controller.get_mouse_pressed()
            self.update_state(pressed_keys, mouse_click_pos)

            time.sleep(1 / self.fps)
