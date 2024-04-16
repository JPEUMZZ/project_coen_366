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
        self.mutex = threading.Lock()

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
        message = f"Global Message: {message}"
        for username, user_details in self.users.items():
            self.server_socket.sendto(message.encode('utf-8'), user_details["address"])

    def listening(self, message, client_address):
        msg = message.decode('utf-8')
        print(f"Message incoming from {client_address}: {message}")

        # registration
        if msg.startswith("REGISTER"):
            parts = message.split()
            if len(parts) == 4:
                _, username, ip, port = parts
                if username in self.users:
                    response = f"REGISTRATION DENIED for {username}. Reason: Username already in use."
                    notification = f"{username} denied registration."
                    print(f"Registration Denied for {username}.")
                    self.send_notification(notification)
                else:
                    self.users[username] = {"IP": ip, "port": port, "address": client_address, "files": []}
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

        # wants to say that it has this file
        elif msg.startswith("UPLOADFILE"):
            _, username, filename = message.split()
            if username in self.users:
                if filename not in self.users[username]["files"]:
                    self.users[username]["files"].append(filename)
                    response = f"{username} uploaded {filename} successfully."
                    notification = f"{username} has uploaded {filename} onto server."
                    self.send_notification(notification)
                else:
                    response = f"File already exists on server under {username}. Did not append."
            else:
                response = f"You do not have permission, as you are not registered."
            self.server_socket.sendto(response.encode('utf-8'), client_address)

        # transferfile, wants a file from someone
        elif msg.startswith("CHECKFILE"):
            _, username, filename = message.split()
            if username in self.users:
                for user in self.users:
                    if filename in self.users[user]["files"]:
                        response = f"File exists on server under {user}. IP: {self.users[user]['IP']} PORT: {self.users[user]['port']}"
                        break
                    else:
                        response = f"File does not exist anywhere. Request for file: {filename} denied."
            self.server_socket.sendto(response.encode('utf-8'), client_address)

        # do nothing here, just taking file from client
        elif msg.startswith("CLIENTCONNECT"): # this message is meant to be sent to other clients
            pass

    def close(self):
        self.server_socket.close()

SERVER_PORT = 3000
server = Server(SERVER_PORT)
server.start()
server.close()