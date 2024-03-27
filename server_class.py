import socket
import sys
import threading

BUFFER_SIZE = 1024

class Server(threading.Thread):
    def __init__(self, port):
        super(server, self).__init__()
        self.sock = socket
        self.HOST_NAME = socket.gethostname()
        self.HOST = self.sock.gethostbyname(self.HOST_NAME)
        self.PORT = port
        self.users = {}
        self.create_socket()

    def create_socket(self):
        try:
            print("Creation of socket in progress...")
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        except socket.error as msg:
            print(f"Error creating socket. Code {str(msg[0])}: {str(msg[1])}")
            sys.exit()

        print("Created socket")
        self.configure_socket()

    def configure_socket(self):
        try:
            print(f"Binding SERVER host {self.HOST} and port {self.PORT}")
            self.sock.socket.bind(self.HOST, self.PORT)

        except socket.error as msg:
            print(f"Binding of socket failed. Code {str(msg[0])}: {str(msg[1])}")
            sys.exit()

        print("Socket configured.")

    def listening(self, client_socket, client_address):
        while True:
            message, client_address = client_socket.recvfrom(BUFFER_SIZE)
            message = message.decode('utf-8')
            print(f"Message from {client_address}: {message}")

            if message.startswith("REGISTER"):
                _, username, ip, port = message.split()
                if username in self.users:
                    response = f"REGISTRATION DENIED for {username}. Reason: Username already in use."
                else:
                    self.users[username] = (ip, port)
                    response = f"REGISTRATION CONFIRMED for {username}."
                client_socket.sendto(response.encode('utf-8'), client_address)

            elif message.startswith("DEREGISTER"):
                _, username = message.split()
                if username in self.users:
                    del self.users[username]
                    response = f"{username} deregistered successfully."
                else:
                    response = f"{username} is not registered."
                client_socket.sendto(response.encode('utf-8'), client_address)
            # threading.Thread(target=handle_client_message, args=(server_socket, client_address)).start()

SERVER_PORT = 3000
server = Server(SERVER_PORT)