import socket


HOST = "127.0.0.1"
PORT = 65432
ENCODING = "utf-8"


class Client:

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOST, PORT))
        self.name = None
        self.client_id = None

        self.communicate()

    def communicate(self):
        response = self.sock.recv(1024).decode(ENCODING)
        print(response)

        # Server is full
        if "full" in response.lower():
            self.sock.close()
            return

        self.name = input("Name: ")
        self.sock.sendall(self.name.encode(ENCODING))

        response = self.sock.recv(1024).decode(ENCODING)
        print(response)

        while True:
            message = input(f"[{self.name.upper()}]: ")
            self.sock.sendall(message.encode(ENCODING))

            if message.lower() == "exit":
                print("Disconnecting from server...")
                break

            response = self.sock.recv(1024).decode(ENCODING)
            print(response)

            shutdown = "Server is shutting down"
            if shutdown in response and shutdown not in message:
                break

        self.sock.close()


if __name__ == "__main__":
    client = Client()



