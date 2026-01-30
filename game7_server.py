import socket
import math
import time
import random
from threading import Thread, Lock

HOST = '0.0.0.0'
PORT = 21001
WIDTH = 800
HEIGHT = 600
FPS = 60
MAX_NPCS = 10
NPC_SPAWN_INTERVAL = 2.0

game_lock = Lock()


class Player:
    def __init__(self, pid, x, y):
        self.id = pid
        self.x = x
        self.y = y
        self.radius = 20
        self.speed = 5
        self.score = 0

    def move(self, left, right, up, down):
        self.x += self.speed * (right - left)
        self.y += self.speed * (down - up)
        self.x = max(self.radius, min(WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(HEIGHT - self.radius, self.y))

    def collides_with(self, npc):
        dist = math.sqrt((self.x - npc.x) ** 2 + (self.y - npc.y) ** 2)
        return dist < self.radius + npc.radius


class NPC:
    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = 15

    def move(self):
        self.x += self.vx
        self.y += self.vy
        if self.x <= self.radius or self.x >= WIDTH - self.radius:
            self.vx = -self.vx
            self.x = max(self.radius, min(WIDTH - self.radius, self.x))
        if self.y <= self.radius or self.y >= HEIGHT - self.radius:
            self.vy = -self.vy
            self.y = max(self.radius, min(HEIGHT - self.radius, self.y))


class GameState:
    def __init__(self):
        self.players = {}
        self.npcs = []
        self.actions = {}
        self.next_player_id = 1
        self.last_npc_spawn = time.time()

    def add_player(self):
        pid = self.next_player_id
        self.next_player_id += 1
        x = random.randint(100, WIDTH - 100)
        y = random.randint(100, HEIGHT - 100)
        self.players[pid] = Player(pid, x, y)
        self.actions[pid] = {}
        return pid

    def remove_player(self, pid):
        if pid in self.players:
            del self.players[pid]
        if pid in self.actions:
            del self.actions[pid]

    def spawn_npc(self):
        if len(self.npcs) >= MAX_NPCS:
            return
        edge = random.randint(0, 3)
        if edge == 0:
            x, y = random.randint(20, WIDTH - 20), 20
        elif edge == 1:
            x, y = WIDTH - 20, random.randint(20, HEIGHT - 20)
        elif edge == 2:
            x, y = random.randint(20, WIDTH - 20), HEIGHT - 20
        else:
            x, y = 20, random.randint(20, HEIGHT - 20)
        vx = random.choice([-1, 1]) * random.randint(2, 4)
        vy = random.choice([-1, 1]) * random.randint(2, 4)
        self.npcs.append(NPC(x, y, vx, vy))

    def update(self):
        now = time.time()
        if now - self.last_npc_spawn >= NPC_SPAWN_INTERVAL:
            self.spawn_npc()
            self.last_npc_spawn = now

        for npc in self.npcs:
            npc.move()

        for pid, player in self.players.items():
            act = self.actions.get(pid, {})
            player.move(
                act.get("left", 0),
                act.get("right", 0),
                act.get("up", 0),
                act.get("down", 0)
            )

        for pid, player in self.players.items():
            for npc in self.npcs[:]:
                if player.collides_with(npc):
                    player.score += 10
                    self.npcs.remove(npc)

    def get_state_for_client(self, pid):
        players_data = []
        for p in self.players.values():
            players_data.append({"id": p.id, "x": p.x, "y": p.y, "score": p.score})
        npcs_data = []
        for n in self.npcs:
            npcs_data.append({"x": n.x, "y": n.y, "r": n.radius})
        return {"self": pid, "players": players_data, "npcs": npcs_data}


game_state = GameState()


def handle_client(conn, pid):
    print(f"Player {pid} connected")
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            try:
                actions = eval(data.decode())
                with game_lock:
                    game_state.actions[pid] = actions
                    state = game_state.get_state_for_client(pid)
                conn.sendall(str(state).encode())
            except Exception as e:
                print(f"Error processing data from player {pid}: {e}")
                break
    except Exception as e:
        print(f"Connection error with player {pid}: {e}")
    finally:
        with game_lock:
            game_state.remove_player(pid)
        print(f"Player {pid} disconnected")


def accept_connections():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    print(f"Server listening on {HOST}:{PORT}")
    while True:
        conn, addr = s.accept()
        with game_lock:
            pid = game_state.add_player()
        Thread(target=handle_client, args=(conn, pid), daemon=True).start()


def game_loop():
    while True:
        with game_lock:
            game_state.update()
        time.sleep(1 / FPS)


if __name__ == "__main__":
    Thread(target=accept_connections, daemon=True).start()
    game_loop()
