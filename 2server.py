import os
import socket
import sys
import threading

from datetime import datetime


HOST = "127.0.0.1"
PORT = 65432
MAX_CLIENTS = 1  # Limit the number of clients that can connect to server.

ENCODING = "utf-8"


class Server:
    def __init__(self):
        self.sock = self.setup()

        self.cache = {}
        self.client_count = 0
        self.client_list = [0] * MAX_CLIENTS
        self.clients = []
        self.connection_count = 0
        self.lock = threading.Lock()
        self.running = True

    def setup(self) -> socket.socket:
        sock = socket.socket()
        sock.bind((HOST, PORT))
        return sock

    def log(
        self,
        message: str,
        shutdown: bool = False,
        is_client: bool = False,
        client_id: int = 0,
    ) -> None:
        """Clean server logging."""
        with self.lock:
            if shutdown:
                sys.stdout.write(f"\r[SERVER]: {message}\n")
                sys.stdout.flush()

            elif is_client:
                sys.stdout.write(f"\r[CLIENT {client_id}]: {message}\n")
                sys.stdout.write("[SERVER]: ")
                sys.stdout.flush()
            else:
                sys.stdout.write(f"\r[SERVER]: {message}\n")
                sys.stdout.write("[SERVER]: ")
                sys.stdout.flush()

    def start(self) -> None:
        self.log("Running.")
        self.sock.listen(MAX_CLIENTS)
        threading.Thread(target=self.monitor_exit, daemon=True).start()

        while self.running:
            try:
                self.sock.settimeout(1)
                connection, address = self.sock.accept()

                if all(client == 1 for client in self.client_list):
                    connection.sendall(
                        b"[SERVER]: The server is full. Try again later."
                    )
                    connection.close()
                    continue

                connection.sendall(b"[SERVER] Enter your name below.")
                name = connection.recv(1024).decode(ENCODING)

                # Find next available client_id
                for i, client in enumerate(self.client_list):
                    if client == 0:
                        self.client_list[i] = 1
                        client_id = i + 1
                        break

                self.connection_count += 1
                self.client_count += 1

                self.clients.append(connection)
                self.cache[self.connection_count] = {
                    "name": name,
                    "client_id": client_id,
                    "address": address,
                    "connected": str(datetime.now()),
                    "disconnected": None,
                    "connection_number": self.connection_count,
                }

                self.log(
                    f"New client {name} connected as [CLIENT {client_id} by {address}]"
                )

                threading.Thread(
                    target=self.handler,
                    args=(connection, client_id, self.connection_count),
                    daemon=True,
                ).start()

                connection.sendall(f"Welcome {name}!".encode(ENCODING))

            except socket.timeout:
                continue

    def handler(
        self, sock: socket.socket, client_id: int, connection_count: int
    ) -> None:
        connected = True

        while connected:
            try:
                message = sock.recv(1024).decode(ENCODING)
                if not message:
                    break

                message = message.lower()

                if message == "exit":
                    connected = False
                    self.cache[connection_count]["disconnected"] = str(datetime.now())

                elif message == "status":
                    sock.sendall(f"[SERVER]: {str(self.cache)}".encode(ENCODING))

                elif message == "list":
                    files = os.listdir(os.curdir)
                    sock.sendall(f"[SERVER]: {str(files)}".encode(ENCODING))

                    file = sock.recv(1024).decode(ENCODING)

                    if file in files:
                        with open(file) as f:
                            stream = f.read()

                        sock.sendall(stream.encode(ENCODING))

                    else:
                        sock.sendall(
                            f"[SERVER]: File {file} does not exist.".encode(ENCODING)
                        )

                else:
                    self.log(message, is_client=True, client_id=client_id)
                    sock.sendall(f"[SERVER]: {message}ACK".encode(ENCODING))

            except Exception:
                break

        self.log(f"Client {client_id} disconnected.")
        sock.close()

        self.clients.remove(sock)
        self.client_list[client_id - 1] = 0

    def monitor_exit(self) -> None:
        while True:
            sys.stdout.write("\r[SERVER]: ")
            sys.stdout.flush()
            cmd = input()
            if cmd.lower() == "exit":
                self.shutdown()
                break

    def shutdown(self) -> None:
        self.log("Shutting down...", True)

        self.running = False  # Stop accepting new clients

        # Close all active client sockets
        for client in self.clients:
            try:
                client.sendall(b"[SERVER]: Server is shutting down. Disconnecting...")
                client.close()
            except Exception:
                pass

        self.sock.close()
        self.log("Shutdown successful.", True)


if __name__ == "__main__":
    server = Server()
    server.start()
