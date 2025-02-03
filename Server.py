import socket
import threading
import datetime

# add comments before handing in

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server
max_clients = 3
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
client_cache = {}

def start_server():
    print("Server started.")
    server_socket.listen(max_clients)
    while True:
        if threading.active_count() - 1 <= max_clients:
            client_socket, address = server_socket.accept()

            client_number = threading.active_count()
            client_cache[client_number] = {"connected": datetime.datetime.now(), "disconnected": None}

            print(f"Client{client_number} connected.")
            server_thread = threading.Thread(target=handle_client, args=(client_socket,client_number))
            server_thread.start()



def handle_client(client_socket, client_number):

    connected = True
    while connected:
        try:
            msg = client_socket.recv(1024).decode("utf-8")
            if msg == "exit":
                connected = False
                client_cache[client_number]["disconnected"] = datetime.datetime.now()
                print(f"Client{client_number} Disconnected.")

            elif msg == "status":
                status_msg = str(client_cache)
                client_socket.sendall(status_msg.encode("utf-8"))
            else:
                client_socket.sendall(f"{msg}ACK".encode("utf-8"))
        except:
                connected = False
    client_socket.close()

if __name__ == '__main__':
    start_server()