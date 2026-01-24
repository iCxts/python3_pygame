import time
import math

import pygame
import random

color_list = ['black', 'red', 'white', 'blue', 'cyan', 'magenta', 'orange', 'purple']
pygame.font.init()
font = pygame.font.SysFont('Arial', 30)

NPC_SPAWN_INTERVAL = 2000
MAX_NPCS = 20


class GameField:
    def __init__(self, x_min, y_min, x_max, y_max):
        self.x_min = x_min
        self.y_min = y_min
        self.x_max = x_max
        self.y_max = y_max

    def clamp(self, x, y):
        return (max(self.x_min, min(self.x_max, x)), max(self.y_min, min(self.y_max, y)),
                self.x_min > x or self.x_max < x, self.y_min > y or self.y_max < y)

    def is_inside(self, x, y):
        return self.x_min <= x <= self.x_max and self.y_min <= y <= self.y_max


class Player:
    def __init__(self, x, y, speed_x=1, speed_y=1):
        self.x = x
        self.y = y
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.angle = 0
        self.rotation_speed = 5

    def move(self, left, right, up, down, game_field):
        self.x += self.speed_x * right - self.speed_x * left
        self.y += self.speed_y * down - self.speed_y * up
        self.x, self.y, _, _ = game_field.clamp(self.x, self.y)

    def rotate(self, rotate_left, rotate_right):
        if rotate_left:
            self.angle -= self.rotation_speed
        if rotate_right:
            self.angle += self.rotation_speed
        self.angle = self.angle % 360

    def get_direction(self):
        angle_rad = math.radians(self.angle)
        return math.cos(angle_rad), math.sin(angle_rad)


class NPC:
    def __init__(self, x, y, speed_x=1, speed_y=1):
        self.x = x
        self.y = y
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.radius = 20

    def move(self, game_field):
        self.x += self.speed_x
        self.y += self.speed_y
        self.x, self.y, x_edge, y_edge = game_field.clamp(self.x, self.y)
        if x_edge:
            self.speed_x = -self.speed_x
        if y_edge:
            self.speed_y = -self.speed_y


class Bullet:
    def __init__(self, x, y, direction_x, direction_y, speed=10):
        self.x = x
        self.y = y
        self.direction_x = direction_x
        self.direction_y = direction_y
        self.speed = speed
        self.radius = 5

    def move(self):
        self.x += self.direction_x * self.speed
        self.y += self.direction_y * self.speed

    def is_outside(self, game_field):
        return not game_field.is_inside(self.x, self.y)

    def hits(self, npc):
        distance = math.sqrt((self.x - npc.x) ** 2 + (self.y - npc.y) ** 2)
        return distance < (self.radius + npc.radius)


class GameEngine:
    def __init__(self, graph_engine, game_field, player, npcs, *, fps=60):
        self.graph_engine = graph_engine
        self.game_field = game_field
        self.player = player
        self.npcs = npcs
        self.bullets = []
        self.fps = fps
        self.clock = pygame.time.Clock()
        self.last_spawn_time = pygame.time.get_ticks()
        self.fire_cooldown = 200
        self.last_fire_time = 0

    def spawn_npc(self):
        if len(self.npcs) >= MAX_NPCS:
            return
        edge = random.randint(0, 3)
        if edge == 0:
            x = random.randint(self.game_field.x_min, self.game_field.x_max)
            y = self.game_field.y_min + 20
        elif edge == 1:
            x = self.game_field.x_max - 20
            y = random.randint(self.game_field.y_min, self.game_field.y_max)
        elif edge == 2:
            x = random.randint(self.game_field.x_min, self.game_field.x_max)
            y = self.game_field.y_max - 20
        else:
            x = self.game_field.x_min + 20
            y = random.randint(self.game_field.y_min, self.game_field.y_max)
        speed_x = random.randint(1, 4) * random.choice([-1, 1])
        speed_y = random.randint(1, 4) * random.choice([-1, 1])
        self.npcs.append(NPC(x, y, speed_x, speed_y))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def fire_bullet(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_fire_time >= self.fire_cooldown:
            dir_x, dir_y = self.player.get_direction()
            bullet_x = self.player.x + dir_x * 25
            bullet_y = self.player.y + dir_y * 25
            self.bullets.append(Bullet(bullet_x, bullet_y, dir_x, dir_y, speed=15))
            self.last_fire_time = current_time

    def update_bullets(self):
        bullets_to_remove = []
        npcs_to_remove = []
        for bullet in self.bullets:
            bullet.move()
            if bullet.is_outside(self.game_field):
                bullets_to_remove.append(bullet)
                continue
            for npc in self.npcs:
                if bullet.hits(npc):
                    bullets_to_remove.append(bullet)
                    npcs_to_remove.append(npc)
                    break
        for bullet in bullets_to_remove:
            if bullet in self.bullets:
                self.bullets.remove(bullet)
        for npc in npcs_to_remove:
            if npc in self.npcs:
                self.npcs.remove(npc)

    def update_state(self, keys):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_spawn_time >= NPC_SPAWN_INTERVAL:
            self.spawn_npc()
            self.last_spawn_time = current_time

        for npc in self.npcs:
            npc.move(self.game_field)

        self.player.move(keys[pygame.K_a], keys[pygame.K_d], keys[pygame.K_w], keys[pygame.K_s], self.game_field)
        self.player.rotate(keys[pygame.K_LEFT], keys[pygame.K_RIGHT])

        if keys[pygame.K_SPACE]:
            self.fire_bullet()

        self.update_bullets()

        if len(self.npcs) == 0:
            text_surface = font.render('YOU WIN', True, (255, 255, 255))
            self.graph_engine.render_text(640, 360, text_surface)
            self.graph_engine.show_frame()
            time.sleep(3)
            self.running = False
            return

        for npc in self.npcs:
            if ((self.player.x >= npc.x - 20 and self.player.x <= npc.x + 20)
                and (self.player.y >= npc.y - 20 and self.player.y <= npc.y + 20)):
                text_surface = font.render('YOU FUCKING DIED', True, (255, 255, 255))
                self.graph_engine.render_text(640, 360, text_surface)
                self.graph_engine.show_frame()
                time.sleep(3)
                self.running = False
                return

        if keys[pygame.K_q]:
            self.running = False

    def render_state(self):
        self.graph_engine.start_frame()
        self.graph_engine.render_player(self.player.x, self.player.y, 20, self.player.angle, 'green')
        for npc in self.npcs:
            self.graph_engine.render_circle(npc.x, npc.y, npc.radius, 'red')
        for bullet in self.bullets:
            self.graph_engine.render_circle(bullet.x, bullet.y, bullet.radius, 'yellow')
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

    def render_player(self, x, y, radius, angle, color):
        pygame.draw.circle(self.screen, color, (x, y), radius)
        angle_rad = math.radians(angle)
        end_x = x + math.cos(angle_rad) * (radius + 15)
        end_y = y + math.sin(angle_rad) * (radius + 15)
        pygame.draw.line(self.screen, 'white', (x, y), (end_x, end_y), 3)
        triangle_size = 8
        tip_x = end_x + math.cos(angle_rad) * triangle_size
        tip_y = end_y + math.sin(angle_rad) * triangle_size
        left_x = end_x + math.cos(angle_rad + 2.5) * triangle_size
        left_y = end_y + math.sin(angle_rad + 2.5) * triangle_size
        right_x = end_x + math.cos(angle_rad - 2.5) * triangle_size
        right_y = end_y + math.sin(angle_rad - 2.5) * triangle_size
        pygame.draw.polygon(self.screen, 'white', [(tip_x, tip_y), (left_x, left_y), (right_x, right_y)])

    def render_text(self, x, y, text_surface):
        self.screen.blit(text_surface, (x, y))


if __name__ == "__main__":
    pygame.init()
    game_field = GameField(0, 0, 1280, 720)
    player = Player(640, 360, speed_x=8, speed_y=8)
    npcs = [NPC(100, 100, 3, 3)]
    graph_engine = PygameGraphicsEngine(1280, 720)
    game_engine = GameEngine(graph_engine, game_field, player, npcs, fps=60)
    game_engine.run_game()
