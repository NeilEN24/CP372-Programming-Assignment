import socket
import threading
import datetime

# add comments before handing in

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server
max_clients = 3


def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((HOST, PORT))
        print(f"Connected to server on {HOST}:{PORT}.")
        while True:
            msg = input("Enter message: ")
            client_socket.sendall(msg.encode("utf-8"))
            if msg == "quit":
                break
            msg_return = client_socket.recv(1024).decode("utf-8")
            print(msg_return)
    except Exception as e:
        print("Connection failed.")
    finally:
        client_socket.close()
        print("Connection closed.")


if __name__ == '__main__':
    start_client()

