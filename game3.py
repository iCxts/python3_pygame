import time

import pygame
import random

#config
color_list = ['black', 'red', 'white', 'blue', 'cyan', 'magenta', 'orange', 'purple']
pygame.font.init()
font = pygame.font.SysFont('Arial', 30)

class GameField:
    def __init__(self, x_min, y_min, x_max, y_max):
        self.x_min = x_min
        self.y_min = y_min
        self.x_max = x_max
        self.y_max = y_max

    def clamp(self, x, y):
        return (max(self.x_min, min(self.x_max, x)), max(self.y_min, min(self.y_max, y)),
                self.x_min > x or self.x_max < x, self.y_min > y or self.y_max < y)


class Player:
    def __init__(self, x, y, speed_x=1, speed_y=1):
        self.x = x
        self.y = y
        self.speed_x = speed_x
        self.speed_y = speed_y

    def move(self, left, right, up, down, game_field):
        self.x += self.speed_x * right - self.speed_x * left
        self.y += self.speed_y * down - self.speed_y * up

        self.x, self.y, _, _ = game_field.clamp(self.x, self.y)


class NPC:
    def __init__(self, x, y, speed_x=1, speed_y=1):
        self.x = x
        self.y = y
        self.speed_x = speed_x
        self.speed_y = speed_y

    def move(self, game_field):
        self.x += self.speed_x
        self.y += self.speed_y

        self.x, self.y, x_edge, y_edge = game_field.clamp(self.x, self.y)

        if x_edge:
            self.speed_x = -self.speed_x

        if y_edge:
            self.speed_y = -self.speed_y


class GameEngine:
    def __init__(self, graph_engine, game_field, player, npc, *, fps=60):
        self.graph_engine = graph_engine
        self.game_field = game_field
        self.player = player
        self.npc = npc
        self.fps = fps
        self.clock = pygame.time.Clock()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update_state(self, keys):
        self.npc.move(self.game_field)

        self.player.move(keys[pygame.K_a], keys[pygame.K_d], keys[pygame.K_w], keys[pygame.K_s], self.game_field)

        if ((self.player.x >= self.npc.x - 20 and self.player.x <= self.npc.x + 20)
            and (self.player.y >= self.npc.y - 20 and self.player.y <= self.npc.y + 20)):
            text_surface = font.render('YOU FUCKING DIED', True, (255, 255, 255))
            self.graph_engine.render_text(640, 360, text_surface)
            self.graph_engine.show_frame()
            time.sleep(3)
            self.running = False


        if keys[pygame.K_q]:
            self.running = False

    def render_state(self):
        self.graph_engine.start_frame()

        self.graph_engine.render_circle(self.player.x, self.player.y, 20, color_list[random.randint(0, 7)])
        self.graph_engine.render_circle(self.npc.x, self.npc.y, 20, color_list[random.randint(0, 7)])

        self.graph_engine.show_frame()

    def run_game(self):
        self.running = True
        while self.running:
            self.handle_events()
            keys = pygame.key.get_pressed()
            self.update_state(keys)
            self.render_state()

            self.clock.tick(self.fps)

        pygame.quit()


class PygameGraphicsEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Game")

    def start_frame(self):
        self.screen.fill('black')

    def show_frame(self):
        pygame.display.flip()

    def render_circle(self, x, y, radius, color):
        pygame.draw.circle(self.screen, color, (x, y), radius)

    def render_text(self, x, y, text_surface):
        self.screen.blit(text_surface, (x, y))


if __name__ == "__main__":
    pygame.init()

    game_field = GameField(0, 0, 1280, 720)
    player = Player(50, 50, speed_x=15, speed_y=15)
    npc = NPC(70, 70, 3, 3)

    graph_engine = PygameGraphicsEngine(1280, 720)
    game_engine = GameEngine(graph_engine, game_field, player, npc, fps=60)
    game_engine.run_game()
