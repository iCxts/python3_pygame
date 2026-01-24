import socket
from threading import Thread

HOST = '0.0.0.0'
PORT = 21001
s = None

connected_clients_number = 0


def client_processor(conn):
    global connected_clients_number

    while True:
        message_received = ""
        data = conn.recv(4096)
        if not data:
            print("Client disconnected")
            connected_clients_number -= 1
            break

        message_received += data.decode()

        print("Received message from client: ", message_received)

        message = f"Hello, client! Total clients connected: {connected_clients_number}"
        conn.send((message).encode())

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Socket created")
except OSError as msg:
    s = None
    print(f"Error creating socket: {msg}")
    exit(1)

try:
    s.bind((HOST, PORT))
    s.listen()
    print("Socket bound and listening")
except OSError as msg:
    print("Error binding/listening!")
    s.close()
    exit(1)

while True:
    conn, addr = s.accept()
    print("Client connected from address: ", addr)
    connected_clients_number += 1
    client_thread = Thread(target=client_processor, args=(conn,))
    client_thread.start()

s.close()
print("Server finished")
