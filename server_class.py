import socket
import sys
import threading
import json

BUFFER_SIZE = 1024

class Server(threading.Thread):
    def __init__(self, port):
        super(Server, self).__init__()
        self.server_socket = socket
        self.HOST_NAME = socket.gethostname()
        self.HOST = self.server_socket.gethostbyname(self.HOST_NAME) # host
        self.PORT = port # port number
        self.users = {}
        self.create_socket()

    def create_socket(self):
        try:
            print("Creation of socket in progress...")
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # creates a UDP socket

        except socket.error as msg:
            print(f"Error creating socket. Code {str(msg[0])}: {str(msg[1])}")
            sys.exit()

        print("Created socket")
        self.configure_socket() # bind the socket

    def configure_socket(self):
        try:
            self.server_socket.bind((self.HOST, self.PORT)) # server IP and port number

        except socket.error as msg:
            print(f"Binding of socket failed. Code {str(msg[0])}: {str(msg[1])}")
            sys.exit()

        print("Socket configured. Server is up.")
        print(f"UDP server is listening on {self.HOST}:{self.PORT}")

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

                    with open("clients.txt", 'w') as fout:
                        data = {
                            username: [client_address, ip, port, [f"file1.txt", f"file2.txt"]]
                        }
                        json.dump(data, fout)

                client_socket.sendto(response.encode('utf-8'), client_address)

            elif message.startswith("DEREGISTER"):
                _, username = message.split()
                user_list = {}
                with open("clients.txt", 'r') as fin:
                    user_list = json.load(fin)
                if username in user_list:
                    del user_list[username]
                    response = f"{username} deregistered successfully."
                    with open("clients.txt", 'w') as fout:
                        json.dump(user_list, fout)
                else:
                    response = f"{username} is not registered."
                client_socket.sendto(response.encode('utf-8'), client_address)
            # threading.Thread(target=handle_client_message, args=(server_socket, client_address)).start()

    def close(self):
        self.server_socket.close()

SERVER_PORT = 3000
server = Server(SERVER_PORT)
server.start()
while True:
    message, client_address = server.server_socket.recvfrom(BUFFER_SIZE)
    threading.Thread(target=server.listening, args=(server.server_socket, client_address)).start()

server.close()