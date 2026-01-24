import socket
from threading import Thread

from characters import Player, NPC
from game_field import GameField
from server_game_engine import ServerGameEngine

connected_clients_number = 0


def player_data_exchange(conn, player_id, game_engine):
    while True:
        # print("Waiting for player actions...")
        try:
            player_actions_data = conn.recv(1024)
            if not player_actions_data:
                print("Player disconnected")
                break

            player_actions = eval(player_actions_data.decode())
            # print("Player actions received", player_actions)
            game_engine.set_player_actions(player_id, player_actions)

            game_state_data = game_engine.get_game_state_data()
            game_engine.set_player_actions(player_id, player_actions_data.decode())

            game_state_data["self"] = player_id
            conn.sendall(str(game_state_data).encode())
            # print("State sent to player")
        except Exception as e:
            print(f"Error exchanging data: {e}")
            break

    game_engine.remove_player(player_id)



def conection_listener_thread_function(game_engine):
    global connected_clients_number

    HOST = '0.0.0.0'
    PORT = 21001
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen()

    while True:
        print("Waiting for player connection...")
        conn, addr = s.accept()
        connected_clients_number += 1
        print(f"Player connected and assigned ID: {connected_clients_number}")

        new_player = Player(connected_clients_number, 50, 50)
        game_engine.add_player(new_player)

        client_thread = Thread(target=player_data_exchange, args=(conn, connected_clients_number, game_engine))
        client_thread.start()


if __name__ == "__main__":
    game_field = GameField(0, 0, 600, 600)
    # player = Player(1, 50, 50, speed_x=3, speed_y=3)
    npcs = [NPC(70, 70, 2, 1)]

    game_engine = ServerGameEngine(
        game_field,
        [],
        npcs,
        fps=60)

    players_data_exchange_thread = Thread(target=conection_listener_thread_function, args=(game_engine,))
    players_data_exchange_thread.start()

    game_engine.run_game()
