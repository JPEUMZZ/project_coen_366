import socket
import sys
import threading
import time
import os

BUFFER_SIZE = 1024

class Server(threading.Thread):
    def __init__(self, port):
        super(Server, self).__init__()
        self.server_socket = socket
        self.HOST_NAME = socket.gethostname()
        self.SERVER_IP = self.server_socket.gethostbyname(self.HOST_NAME) # host
        self.PORT = port # port number
        self.users = {}

        # if os.path.exists("backup.txt") and os.path.getsize("backup.txt"):
        #     with open("backup.txt", "r") as file:
        #         for line in file:
        #             parts = line.strip().split()
        #             username = parts[0]
        #             ip = parts[1]
        #             port = int(parts[2])
        #             address = (ip, port)
        #             files = parts[4:] if len(parts) > 4 else []
        #             self.users[username] = {"IP": ip, "port": port, "address": address, "files": files}


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
        print(f"Message incoming from {client_address}: {msg}")

        # registration
        if msg.startswith("REGISTER"):
            parts = msg.split()
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
            self.send_update()
            self.backup()

        # deregister
        elif msg.startswith("DE-REGISTER"):
            _, req, username = msg.split()
            if username in self.users:
                del self.users[username]
                response = f"DE-REGISTER {req} {username}."
                self.server_socket.sendto(response.encode('utf-8'), client_address)
                self.send_update()
                self.backup()

        # update IP address
        elif msg.startswith("UPDATE-CONTACT"):
            parts = msg.split()
            if len(parts) == 5:
                _, req, username, new_ip, new_udp_socket = parts
                files = self.users[username]['files']
                if username in self.users:
                    self.users[username] = {"IP": new_ip, "port": new_udp_socket, "address": client_address, "files": files}
                    response = f"UPDATE-CONFIRMED {req} {username} {new_ip} {new_udp_socket}"
                else:
                    response = f"UPDATE-DENIED {req} {username}: User not found."
                self.server_socket.sendto(response.encode('utf-8'), client_address)
            self.send_update()
            self.backup()

        # request info
        elif msg.startswith("REQUEST-INFO"):
            user_update = "USERS INFORMATION: "
            for username, user_details in self.users.items():
                self.server_socket.sendto(user_update.encode('utf-8'), user_details["address"])

            for username, user_details in self.users.items():
                user_info = f"Username: {username} IP: {user_details['IP']} Port: {user_details['port']} Files: {user_details['files']}"
                for username, user_details in self.users.items():
                    self.server_socket.sendto(user_info.encode('utf-8'), user_details["address"])

        # publish file to server
        elif msg.startswith("PUBLISH"):
            _, req, username, filename = msg.split()
            if username in self.users:
                if filename not in self.users[username]["files"]:
                    self.users[username]["files"].append(filename)
                    response = f"PUBLISHED {req}"
                else:
                    response = f"PUBLISH-DENIED {req} Reason: File already exists on server under {username}."
            else:
                response = f"PUBLISH-DENIED {req} Reason: You do not have permission, as you are not registered."
            self.server_socket.sendto(response.encode('utf-8'), client_address)
            self.send_update()
            self.backup()

        # delete file
        elif msg.startswith("REMOVE"):
            _, req, username, filename = msg.split()
            if username in self.users:
                if filename in self.users[username]["files"]:
                    self.users[username]["files"].remove(filename)
                    response = f"REMOVED {req}"
                else:
                    response = f"REMOVE-DENIED {req} Reason: File does not exist under {username}. Could not delete file."
            else:
                response = f"REMOVE-DENIED {req} Reason: You do not have permission, as you are not registered."
            self.server_socket.sendto(response.encode('utf-8'), client_address)
            self.send_update()
            self.backup()

        # transferfile, wants a file from someone
        elif msg.startswith("CHECKFILE"):
            _, username, filename = msg.split()
            if username in self.users:
                for user in self.users:
                    if filename in self.users[user]["files"]:
                        response = f"File exists on server under {user}. IP: {self.users[user]['IP']} PORT: {self.users[user]['port']}"
                        break
                    else:
                        response = f"File does not exist anywhere. Request for file: {filename} denied."
            self.server_socket.sendto(response.encode('utf-8'), client_address)

    def send_update(self):
        if self.users:
            user_update = "UPDATE: "
            for username, user_details in self.users.items():
                self.server_socket.sendto(user_update.encode('utf-8'), user_details["address"])

            for username, user_details in self.users.items():
                user_info = f"Username: {username} IP: {user_details['IP']} Port: {user_details['port']} Files: {user_details['files']}"
                for username, user_details in self.users.items():
                    self.server_socket.sendto(user_info.encode('utf-8'), user_details["address"])

    def update(self):
        while True:
            if self.users:
                user_update = "UPDATE: "
                for username, user_details in self.users.items():
                    self.server_socket.sendto(user_update.encode('utf-8'), user_details["address"])

                for username, user_details in self.users.items():
                    user_info = f"Username: {username} IP: {user_details['IP']} Port: {user_details['port']} Files: {user_details['files']}"
                    for username, user_details in self.users.items():
                        self.server_socket.sendto(user_info.encode('utf-8'), user_details["address"])
            time.sleep(300)

    def backup(self):
        pass
        # with open("backup.txt", "w") as file:
        #     for username, user_details in self.users.items():
        #         files_str = ' '.join(str(file_name) for file_name in user_details['files'])
        #         line = f"{username} {user_details['IP']} {user_details['port']} {files_str}\n"
        #         file.write(line)

    def close(self):
        self.server_socket.close()

SERVER_PORT = 3000
server = Server(SERVER_PORT)
server.close()