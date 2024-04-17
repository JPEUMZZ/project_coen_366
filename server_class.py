import socket
import sys
import threading
import time

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
        update_thread = threading.Thread(target=self.update).start()
        while True: # listens on socket, then creates thread for each received
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
            if len(parts) == 5:
                _, req, username, ip, port = parts
                if username in self.users:
                    response = f"REGISTRATION-DENIED {req} Reason: Username already in use."
                else:
                    self.users[username] = {"IP": ip, "port": port, "address": client_address, "files": []}
                    response = f"REGISTERED {req}"
            else:
                response = f"REGISTRATION-DENIED {parts[1]} Reason: Invalid registration message format."
            self.server_socket.sendto(response.encode('utf-8'), client_address)
            threading.Thread(target=self.send_update)

        # deregister
        elif msg.startswith("DE-REGISTER"):
            _, req, username = message.split()
            if username in self.users:
                del self.users[username]
                response = f"DE-REGISTER {req} {username}."
                self.server_socket.sendto(response.encode('utf-8'), client_address)
                self.update()

        # update IP address
        elif msg.startswith("UPDATE-CONTACT"):
            parts = message.split()
            if len(parts) == 5:
                _, req, username, new_ip, new_udp_socket = parts
                if username in self.users:
                    self.users[username] = {"IP": new_ip, "port": new_udp_socket, "address": client_address}
                    response = f"UPDATE-CONFIRMED {req} {username} {new_ip} {new_udp_socket}"
                    self.update()
                else:
                    response = f"UPDATE-DENIED {req} {username}: User not found."
                self.server_socket.sendto(response.encode('utf-8'), client_address)

        # request info
        elif msg.startswith("REQUEST-INFO"):
            user_update = "USERS INFORMATION: "
            for username, user_details in self.users.items():
                self.server_socket.sendto(user_update.encode('utf-8'), user_details["address"])

            for username, user_details in self.users.items():
                user_info = f"Username: {username} IP: {user_details['IP']} Port: {user_details['port']}"
                for username, user_details in self.users.items():
                    self.server_socket.sendto(user_info.encode('utf-8'), user_details["address"])

        # wants to say that it has this file
        elif msg.startswith("PUBLISH"):
            _, req, username, filename = message.split()
            if username in self.users:
                if filename not in self.users[username]["files"]:
                    self.users[username]["files"].append(filename)
                    response = f"Published {req}"
                    self.update()
                else:
                    response = f"PUBLISH-DENIED {req} Reason: File already exists on server under {username}."
            else:
                response = f"PUBLISH-DENIED {req} Reason: You do not have permission, as you are not registered."
            self.server_socket.sendto(response.encode('utf-8'), client_address)

        # delete file
        elif msg.startswith("REMOVE"):
            _, req, username, filename = message.split()
            if username in self.users:
                if filename in self.users[username]["files"]:
                    self.users[username]["files"].remove(filename)
                    response = f"REMOVED {req}"
                    self.update()
                else:
                    response = f"REMOVE-DENIED {req} Reason: File does not exist under {username}. Could not delete file."
            else:
                response = f"REMOVE-DENIED {req} Reason: You do not have permission, as you are not registered."
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

    def send_update(self):
        while True:
            if self.users:
                user_update = "UPDATE: "
                for username, user_details in self.users.items():
                    self.server_socket.sendto(user_update.encode('utf-8'), user_details["address"])

                for username, user_details in self.users.items():
                    user_info = f"Username: {username} IP: {user_details['IP']} Port: {user_details['port']}"
                    for username, user_details in self.users.items():
                        self.server_socket.sendto(user_info.encode('utf-8'), user_details["address"])

    def update(self):
        while True:
            if self.users:
                user_update = "UPDATE: "
                for username, user_details in self.users.items():
                    self.server_socket.sendto(user_update.encode('utf-8'), user_details["address"])

                for username, user_details in self.users.items():
                    user_info = f"Username: {username} IP: {user_details['IP']} Port: {user_details['port']}"
                    for username, user_details in self.users.items():
                        self.server_socket.sendto(user_info.encode('utf-8'), user_details["address"])
            time.sleep(300)

    def close(self):
        self.server_socket.close()

SERVER_PORT = 3000
server = Server(SERVER_PORT)
server.close()