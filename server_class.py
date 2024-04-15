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
        self.SERVER_IP = self.server_socket.gethostbyname(self.HOST_NAME) # host
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

        print("Created socket...")

        try:
            self.server_socket.bind((self.SERVER_IP, self.PORT))  # server IP and port number

        except socket.error as msg:
            print(f"Binding of socket failed. Code {str(msg[0])}: {str(msg[1])}")
            sys.exit()

        print("Socket configured. Server is up.")
        print(f"UDP server is listening on {self.SERVER_IP}:{self.PORT}")
        while True: # listens on socket, then creates thread
            message, client_address = self.server_socket.recvfrom(BUFFER_SIZE)
            threading.Thread(target=self.listening, args=(message, client_address)).start()

    # send notification to everyone on the users list
    def send_notification(self, message):
        for username, user_details in self.users.items():
            self.server_socket.sendto(message.encode('utf-8'), user_details["address"])

    def listening(self, message, client_address):
        msg = message.decode('utf-8').strip()
        print(f"Message incoming from {client_address}: {message}")

        # registration
        if msg.startswith("REGISTER"):
            parts = message.split()
            if len(parts) == 4:
                _, username, ip, port = parts
                if username in self.users:
                    response = f"REGISTRATION DENIED for {username}. Reason: Username already in use."
                    print(f"Registration Denied for {username}.")
                else:
                    self.users[username] = {"IP": ip, "port": port, "address": client_address}
                    response = f"REGISTRATION CONFIRMED for {username}."
                    notification = f"{username} has registered."
                    self.send_notification(notification)
            else:
                response = "Invalid registration message format."
            self.server_socket.sendto(response.encode('utf-8'), client_address)

        # deregister
        elif msg.startswith("DEREGISTER"):
            _, username = message.split()
            if username in self.users:
                del self.users[username]
                response = f"{username} deregistered successfully."
                notification = f"{username} has deregistered."
                self.send_notification(notification)
            else:
                response = f"{username} is not registered."
            self.server_socket.sendto(response.encode('utf-8'), client_address)

        elif msg.startswith("UPDATE-CONTACT"):
            parts = message.split()
            if len(parts) == 4:
                _, username, new_ip, new_udp_socket = parts
                if username in self.users:
                    self.users[username] = {"IP": new_ip, "port": new_udp_socket, "address": client_address}
                    response = f"UPDATE-CONFIRMED {username} {new_ip} {new_udp_socket}"

                else:
                    response = "UPDATE FAILED: User not found."
                self.server_socket.sendto(response.encode('utf-8'), client_address)

    def close(self):
        self.server_socket.close()

SERVER_PORT = 3000
server = Server(SERVER_PORT)
server.start()
server.close()