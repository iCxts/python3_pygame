import math
import pygame
import random

pygame.font.init()
font = pygame.font.SysFont('Arial', 32)

NPC_SPAWN_INTERVAL = 2000
COIN_SPAWN_INTERVAL = 3000
MAX_NPCS = 15
MAX_COINS = 3
BULLET_SPEED = 15
ROTATION_SPEED = 5


class GameField:
    def __init__(self, x_min, y_min, x_max, y_max):
        self.x_min = x_min
        self.y_min = y_min
        self.x_max = x_max
        self.y_max = y_max

    def clamp(self, x, y):
        clamped_x = max(self.x_min, min(self.x_max, x))
        clamped_y = max(self.y_min, min(self.y_max, y))
        hit_x = x < self.x_min or x > self.x_max
        hit_y = y < self.y_min or y > self.y_max
        return clamped_x, clamped_y, hit_x, hit_y

    def is_outside(self, x, y):
        return x < self.x_min or x > self.x_max or y < self.y_min or y > self.y_max

    def random_edge_pos(self):
        edge = random.randint(0, 3)
        if edge == 0:
            return random.randint(self.x_min, self.x_max), self.y_min
        elif edge == 1:
            return self.x_max, random.randint(self.y_min, self.y_max)
        elif edge == 2:
            return random.randint(self.x_min, self.x_max), self.y_max
        else:
            return self.x_min, random.randint(self.y_min, self.y_max)

    def random_coin_pos(self):
        return random.randint(self.x_min + 100, self.x_max - 100), random.randint(self.y_min + 100, self.y_max - 100)


class Player:
    def __init__(self, x, y, speed=10):
        self.x = x
        self.y = y
        self.speed = speed
        self.radius = 20
        self.lives = 3
        self.invincible_until = 0
        self.angle = 0

    def move(self, left, right, up, down, game_field):
        self.x += self.speed * right - self.speed * left
        self.y += self.speed * down - self.speed * up
        self.x, self.y, _, _ = game_field.clamp(self.x, self.y)

    def rotate(self, rotate_left, rotate_right):
        if rotate_left:
            self.angle += ROTATION_SPEED
        if rotate_right:
            self.angle -= ROTATION_SPEED

    def is_invincible(self, current_time):
        return current_time < self.invincible_until

    def take_hit(self, current_time):
        if self.is_invincible(current_time):
            return False
        self.lives -= 1
        self.invincible_until = current_time + 2000
        return self.lives <= 0

    def collides_with(self, obj):
        dist = math.sqrt((self.x - obj.x) ** 2 + (self.y - obj.y) ** 2)
        return dist < self.radius + obj.radius

    def fire(self):
        angle_rad = math.radians(self.angle)
        vx = BULLET_SPEED * math.cos(angle_rad)
        vy = -BULLET_SPEED * math.sin(angle_rad)
        return Bullet(self.x, self.y, vx, vy)


class NPC:
    def __init__(self, x, y, speed_x, speed_y):
        self.x = x
        self.y = y
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.radius = 18

    def move(self, game_field):
        self.x += self.speed_x
        self.y += self.speed_y
        self.x, self.y, hit_x, hit_y = game_field.clamp(self.x, self.y)
        if hit_x:
            self.speed_x = -self.speed_x
        if hit_y:
            self.speed_y = -self.speed_y


class Bullet:
    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = 5

    def move(self):
        self.x += self.vx
        self.y += self.vy

    def collides_with(self, obj):
        dist = math.sqrt((self.x - obj.x) ** 2 + (self.y - obj.y) ** 2)
        return dist < self.radius + obj.radius


class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 12


class GameEngine:
    def __init__(self, graph_engine, game_field, player, *, fps=60):
        self.graph_engine = graph_engine
        self.game_field = game_field
        self.player = player
        self.npcs = []
        self.bullets = []
        self.coins = []
        self.score = 0
        self.fps = fps
        self.clock = pygame.time.Clock()
        self.last_npc_spawn = 0
        self.last_coin_spawn = 0
        self.running = False
        self.game_over = False

    def spawn_npc_at(self, x, y):
        if len(self.npcs) >= MAX_NPCS:
            return
        speed_x = random.choice([-1, 1]) * random.randint(2, 5)
        speed_y = random.choice([-1, 1]) * random.randint(2, 5)
        self.npcs.append(NPC(x, y, speed_x, speed_y))

    def spawn_npc_random(self):
        if len(self.npcs) >= MAX_NPCS:
            return
        x, y = self.game_field.random_edge_pos()
        self.spawn_npc_at(x, y)

    def spawn_coin(self):
        if len(self.coins) >= MAX_COINS:
            return
        x, y = self.game_field.random_coin_pos()
        self.coins.append(Coin(x, y))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.game_over:
                    self.restart()
                elif event.key == pygame.K_SPACE and not self.game_over:
                    self.bullets.append(self.player.fire())
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and not self.game_over:
                    self.spawn_npc_at(event.pos[0], event.pos[1])

    def restart(self):
        self.player.x = self.game_field.x_max / 2
        self.player.y = self.game_field.y_max / 2
        self.player.lives = 3
        self.player.invincible_until = 0
        self.player.angle = 0
        self.npcs.clear()
        self.bullets.clear()
        self.coins.clear()
        self.score = 0
        self.game_over = False

    def update_state(self, keys):
        if self.game_over:
            return

        current_time = pygame.time.get_ticks()

        if current_time - self.last_npc_spawn >= NPC_SPAWN_INTERVAL:
            self.spawn_npc_random()
            self.last_npc_spawn = current_time

        if current_time - self.last_coin_spawn >= COIN_SPAWN_INTERVAL:
            self.spawn_coin()
            self.last_coin_spawn = current_time

        self.player.move(
            keys[pygame.K_a] or keys[pygame.K_LEFT],
            keys[pygame.K_d] or keys[pygame.K_RIGHT],
            keys[pygame.K_w] or keys[pygame.K_UP],
            keys[pygame.K_s] or keys[pygame.K_DOWN],
            self.game_field
        )

        self.player.rotate(keys[pygame.K_e], keys[pygame.K_q])

        for npc in self.npcs:
            npc.move(self.game_field)

        for bullet in self.bullets:
            bullet.move()

        bullets_to_remove = []
        npcs_to_remove = []
        for bullet in self.bullets:
            if self.game_field.is_outside(bullet.x, bullet.y):
                bullets_to_remove.append(bullet)
                continue
            for npc in self.npcs:
                if npc not in npcs_to_remove and bullet.collides_with(npc):
                    bullets_to_remove.append(bullet)
                    npcs_to_remove.append(npc)
                    self.score += 5
                    break

        for bullet in bullets_to_remove:
            if bullet in self.bullets:
                self.bullets.remove(bullet)
        for npc in npcs_to_remove:
            if npc in self.npcs:
                self.npcs.remove(npc)

        for coin in self.coins[:]:
            if self.player.collides_with(coin):
                self.score += 10
                self.coins.remove(coin)

        for npc in self.npcs[:]:
            if self.player.collides_with(npc):
                if self.player.take_hit(current_time):
                    self.game_over = True
                    return
                self.npcs.remove(npc)

        if keys[pygame.K_ESCAPE]:
            self.running = False

    def render_state(self):
        current_time = pygame.time.get_ticks()
        self.graph_engine.start_frame()

        for coin in self.coins:
            self.graph_engine.render_coin(coin.x, coin.y, coin.radius)

        for npc in self.npcs:
            self.graph_engine.render_npc(npc.x, npc.y, npc.radius)

        for bullet in self.bullets:
            self.graph_engine.render_bullet(bullet.x, bullet.y, bullet.radius)

        show_player = not self.player.is_invincible(current_time) or (current_time // 100) % 2 == 0
        if show_player:
            self.graph_engine.render_player(self.player.x, self.player.y, self.player.radius, self.player.angle)

        self.graph_engine.render_hud(self.score, self.player.lives)

        if self.game_over:
            self.graph_engine.render_game_over(self.score)

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
        pygame.display.set_caption("Shooter Game")

    def start_frame(self):
        self.screen.fill((30, 30, 50))

    def show_frame(self):
        pygame.display.flip()

    def render_player(self, x, y, radius, angle):
        pygame.draw.circle(self.screen, (80, 180, 255), (int(x), int(y)), radius)
        pygame.draw.circle(self.screen, (255, 255, 255), (int(x), int(y)), radius, 2)
        angle_rad = math.radians(angle)
        end_x = x + radius * 1.5 * math.cos(angle_rad)
        end_y = y - radius * 1.5 * math.sin(angle_rad)
        pygame.draw.line(self.screen, (255, 255, 0), (int(x), int(y)), (int(end_x), int(end_y)), 4)
        tip_x = x + (radius + 8) * math.cos(angle_rad)
        tip_y = y - (radius + 8) * math.sin(angle_rad)
        pygame.draw.circle(self.screen, (255, 255, 0), (int(tip_x), int(tip_y)), 5)

    def render_npc(self, x, y, radius):
        pygame.draw.circle(self.screen, (255, 80, 80), (int(x), int(y)), radius)
        pygame.draw.circle(self.screen, (255, 200, 200), (int(x), int(y)), radius, 2)

    def render_bullet(self, x, y, radius):
        pygame.draw.circle(self.screen, (255, 255, 100), (int(x), int(y)), radius)

    def render_coin(self, x, y, radius):
        pygame.draw.circle(self.screen, (255, 215, 0), (int(x), int(y)), radius)
        pygame.draw.circle(self.screen, (255, 255, 200), (int(x), int(y)), radius, 2)

    def render_hud(self, score, lives):
        score_text = font.render(f'Score: {score}', True, (255, 255, 255))
        self.screen.blit(score_text, (20, 20))
        lives_text = font.render(f'Lives: {lives}', True, (255, 100, 100))
        self.screen.blit(lives_text, (20, 55))
        controls_text = font.render('WASD:move  Q/E:rotate  SPACE:fire  Click:spawn NPC', True, (150, 150, 150))
        self.screen.blit(controls_text, (20, self.height - 40))

    def render_game_over(self, score):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        game_over_text = font.render('GAME OVER', True, (255, 80, 80))
        text_rect = game_over_text.get_rect(center=(self.width / 2, self.height / 2 - 30))
        self.screen.blit(game_over_text, text_rect)
        score_text = font.render(f'Final Score: {score}', True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(self.width / 2, self.height / 2 + 10))
        self.screen.blit(score_text, score_rect)
        restart_text = font.render('Press R to restart', True, (200, 200, 200))
        restart_rect = restart_text.get_rect(center=(self.width / 2, self.height / 2 + 50))
        self.screen.blit(restart_text, restart_rect)


if __name__ == "__main__":
    pygame.init()
    game_field = GameField(0, 0, 1280, 720)
    player = Player(640, 360, speed=10)
    graph_engine = PygameGraphicsEngine(1280, 720)
    game_engine = GameEngine(graph_engine, game_field, player, fps=60)
    game_engine.run_game()
