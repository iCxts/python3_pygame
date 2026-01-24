import socket

from graphics_engine import PyGameGraphicsEngine
from input_controller import PyGameInputController

HOST = '127.0.0.1'
PORT = 21001

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    print("Connected to server")

    graph_engine = PyGameGraphicsEngine(600, 600)
    input_controller = PyGameInputController()

    while True:
        pkeys = input_controller.get_pressed_keys()

        actions = {}
        if "a" in pkeys:
            actions["left"] = 1
        if "d" in pkeys:
            actions["right"] = 1
        if "w" in pkeys:
            actions["up"] = 1
        if "s" in pkeys:
            actions["down"] = 1

        if "q" in pkeys:
            break

        print("Sending actions...", actions)
        s.send(str(actions).encode())

        print("Waiting for state...")
        state_data = s.recv(1024)
        state = eval(state_data.decode())

        # {1: (97, 3), 'self': 1}
        print("State received:", state)

        graph_engine.start_frame()

        for player_id, positions in state.items():
            if player_id == "self":
                continue
            graph_engine.render_circle(positions[0], positions[1], 20, "green" if player_id == state["self"] else "blue")

        graph_engine.show_frame()

