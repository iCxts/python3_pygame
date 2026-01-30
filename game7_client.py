import socket
import pygame

HOST = '127.0.0.1'
PORT = 21001
WIDTH = 800
HEIGHT = 600

pygame.init()
pygame.font.init()
font = pygame.font.SysFont('Arial', 24)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Multiplayer NPC Eater")
clock = pygame.time.Clock()


def render_state(state, my_id):
    screen.fill((30, 30, 50))

    for npc in state.get("npcs", []):
        pygame.draw.circle(screen, (255, 80, 80), (int(npc["x"]), int(npc["y"])), npc["r"])
        pygame.draw.circle(screen, (255, 200, 200), (int(npc["x"]), int(npc["y"])), npc["r"], 2)

    for p in state.get("players", []):
        if p["id"] == my_id:
            color = (80, 180, 255)
        else:
            color = (80, 255, 80)
        pygame.draw.circle(screen, color, (int(p["x"]), int(p["y"])), 20)
        pygame.draw.circle(screen, (255, 255, 255), (int(p["x"]), int(p["y"])), 20, 2)

    y_offset = 10
    sorted_players = sorted(state.get("players", []), key=lambda x: x["score"], reverse=True)
    for p in sorted_players:
        prefix = ">> " if p["id"] == my_id else ""
        text = font.render(f'{prefix}Player {p["id"]}: {p["score"]}', True, (255, 255, 255))
        screen.blit(text, (WIDTH - 200, y_offset))
        y_offset += 30

    controls = font.render("WASD to move, Q to quit", True, (150, 150, 150))
    screen.blit(controls, (10, HEIGHT - 30))

    pygame.display.flip()


def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((HOST, PORT))
    except ConnectionRefusedError:
        print("Could not connect to server. Make sure game7_server.py is running.")
        return

    print("Connected to server")
    my_id = None
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_q]:
            running = False
            continue

        actions = {}
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            actions["left"] = 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            actions["right"] = 1
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            actions["up"] = 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            actions["down"] = 1

        try:
            s.sendall(str(actions).encode())
            data = s.recv(4096)
            if not data:
                break
            state = eval(data.decode())
            my_id = state.get("self", my_id)
            render_state(state, my_id)
        except Exception as e:
            print(f"Connection error: {e}")
            break

        clock.tick(60)

    s.close()
    pygame.quit()


if __name__ == "__main__":
    main()
