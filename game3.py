import time

import pygame
import random


class GameConfig:
    def __init__(
        self,
        #screen
        screen_width=1280,
        screen_height=720,
        window_title="Game",
        background_color='black',
        fps=60,
        #fonts
        font_name='Arial',
        font_size=30,
        #player 
        player_start_x=50,
        player_start_y=50,
        player_speed_x=15,
        player_speed_y=15,
        player_radius=20,
        #npc
        npc_start_x=70,
        npc_start_y=70,
        npc_speed_x=20,
        npc_speed_y=20,
        npc_radius=20,
        #colliusion 
        collision_radius=20,
        #game over 
        death_message='YOU DIED',
        death_text_color=(255, 255, 255),
        death_screen_delay=3.0,
    ):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.window_title = window_title
        self.background_color = background_color
        self.fps = fps
        self.font_name = font_name
        self.font_size = font_size
        self.player_start_x = player_start_x
        self.player_start_y = player_start_y
        self.player_speed_x = player_speed_x
        self.player_speed_y = player_speed_y
        self.player_radius = player_radius
        self.npc_start_x = npc_start_x
        self.npc_start_y = npc_start_y
        self.npc_speed_x = npc_speed_x
        self.npc_speed_y = npc_speed_y
        self.npc_radius = npc_radius
        self.collision_radius = collision_radius
        self.death_message = death_message
        self.death_text_color = death_text_color
        self.death_screen_delay = death_screen_delay
        self.color_list = ['black', 'red', 'white', 'blue', 'cyan', 'magenta', 'orange', 'purple']

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
    def __init__(self, graph_engine, game_field, player, npcs, config: GameConfig):
        self.graph_engine = graph_engine
        self.game_field = game_field
        self.player = player
        self.npcs = npcs
        self.config = config
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(config.font_name, config.font_size)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update_state(self, keys):
        for npc in self.npcs:
            npc.move(self.game_field)

        self.player.move(keys[pygame.K_a], keys[pygame.K_d], keys[pygame.K_w], keys[pygame.K_s], self.game_field)

        collision_radius = self.config.collision_radius
        for npc in self.npcs:
            if ((self.player.x >= npc.x - collision_radius and self.player.x <= npc.x + collision_radius)
                and (self.player.y >= npc.y - collision_radius and self.player.y <= npc.y + collision_radius)):
                text_surface = self.font.render(self.config.death_message, True, self.config.death_text_color)
                text_x = self.config.screen_width // 2
                text_y = self.config.screen_height // 2
                self.graph_engine.render_text(text_x, text_y, text_surface)
                self.graph_engine.show_frame()
                time.sleep(self.config.death_screen_delay)
                self.running = False
                return

        if keys[pygame.K_q]:
            self.running = False

    def render_state(self):
        self.graph_engine.start_frame()

        colors = self.config.color_list
        self.graph_engine.render_circle(self.player.x, self.player.y, self.config.player_radius, colors[random.randint(0, len(colors) - 1)])
        for npc in self.npcs:
            self.graph_engine.render_circle(npc.x, npc.y, self.config.npc_radius, colors[random.randint(0, len(colors) - 1)])

        self.graph_engine.show_frame()

    def run_game(self):
        self.running = True
        while self.running:
            self.handle_events()
            keys = pygame.key.get_pressed()
            self.update_state(keys)
            self.render_state()

            self.clock.tick(self.config.fps)

        pygame.quit()


class PygameGraphicsEngine:
    def __init__(self, config: GameConfig):
        self.config = config
        self.screen = pygame.display.set_mode((config.screen_width, config.screen_height))
        pygame.display.set_caption(config.window_title)

    def start_frame(self):
        self.screen.fill(self.config.background_color)

    def show_frame(self):
        pygame.display.flip()

    def render_circle(self, x, y, radius, color):
        pygame.draw.circle(self.screen, color, (x, y), radius)

    def render_text(self, x, y, text_surface):
        self.screen.blit(text_surface, (x, y))


if __name__ == "__main__":
    pygame.init()

    config = GameConfig()

    game_field = GameField(0, 0, config.screen_width, config.screen_height)
    player = Player(config.player_start_x, config.player_start_y, speed_x=config.player_speed_x, speed_y=config.player_speed_y)
    npcs = [
        NPC(config.npc_start_x, config.npc_start_y, config.npc_speed_x, config.npc_speed_y),
        NPC(config.screen_width // 2, config.screen_height // 2, config.npc_speed_x, -config.npc_speed_y),
        NPC(config.screen_width - config.npc_start_x, config.screen_height - config.npc_start_y, -config.npc_speed_x, config.npc_speed_y),
    ]

    graph_engine = PygameGraphicsEngine(config)
    game_engine = GameEngine(graph_engine, game_field, player, npcs, config)
    game_engine.run_game()
