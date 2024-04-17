import socket
import sys
import threading
import os
from random import random

BUFFER_SIZE = 1024

class Client(threading.Thread):
    def __init__(self):
        super(Client, self).__init__()
        self.client2server_socket = socket
        self.client2client_socket = socket

        self.HOST_NAME = socket.gethostname()
        self.CLIENT_IP = self.client2server_socket.gethostbyname(self.HOST_NAME)
        self.CLIENT_PORT = None

        self.SERVER_IP = input("Which Server IP would you like to connect to: ")
        self.SERVER_PORT = int(input("What is the server port: "))
        self.username = input(f"Enter you name: ").strip()
        self.CLIENT_PORT = int(input("What is the desired Client2Client port number: "))
        try:
         self.client2server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
         self.client2client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
         self.client2client_socket.bind((self.CLIENT_IP, self.CLIENT_PORT))
         self.tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
         self.tcp.bind((self.CLIENT_IP, self.CLIENT_PORT))
         self.tcp.listen()
        except socket.error as msg:
            print(f"Error creating socket. Code {str(msg[0])}: {str(msg[1])}")
            sys.exit()


        split = self.CLIENT_IP.split('.')
        concat = ''
        for num in split:
            concat += num
        self.RQ = int(concat + str(self.CLIENT_PORT))

        self.register()
        self.listen()

    def listen(self):
        send_thread = threading.Thread(target=self.client_send)
        send_thread.start()

        receive_thread = threading.Thread(target=self.client_receive)
        receive_thread.start()

        clientrecv_udp_thread = threading.Thread(target=self.ClientFileProvider_udp) # as a seperate thread always listening
        clientrecv_udp_thread.start()

    def ClientFileProvider_udp(self):
        while True:
            try:
                data, address = self.client2client_socket.recvfrom(BUFFER_SIZE)
                message = data.decode('utf-8')
                if message:
                    print(f"Received an attempt to connect by {address}: {message}")
                    self.Connection(message, address)

            except Exception as e:
                print(f"Failed to receive data: {e}")
                break

    def Connection(self, message, address):
        try:
            parts = message.split()
            command = parts[0]
            filename = parts[1] if len(parts) > 1 else None

            if command == "CONNECT" and filename:
                if os.path.exists(filename):
                    answer = f"File exists. TCP listening on IP: {self.CLIENT_IP} port: {self.CLIENT_PORT}"
                else:
                    answer = "File does not exist."

                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp:
                    udp.sendto(answer.encode('utf-8'), address)
            else:
                print("Invalid command or filename.")
        except IndexError:
            print("Error parsing message:", message)
        except Exception as e:
            print("Error during connection handling:", e)

    def ClientFileProvider_Thread(self, socketUDP, data, address):
        message = data.decode('utf-8')
        command, filename = message  # make this a separate thread
        if command.startswith("CONNECT"):  # if receive message from client as connect
            print(f"Received an attempt to connect by {address}.")
            try:
                if os.path.exists(filename):
                    answer = input(f"File {filename} is being requested by {address}. "
                                   f"Do we send it? (ACCEPT/REJECT): ")
                    messageSend = answer.upper().encode('utf-8') # send ACCEPT through UDP
                    if answer.upper() == "ACCEPT":
                        socketUDP.sendto(messageSend, address)
                        self.start_sender(address, filename)

                messageSend = f"REJECT"  # auto reject if file doesnt exist
                socketUDP.sendto(messageSend.encode('utf-8'), address)

            except Exception as e:
                print(f'Error in receiving message: {e}')

    def register(self):
        self.RQ += 1
        message = f"REGISTER {self.RQ} {self.username} {self.CLIENT_IP} {self.CLIENT_PORT}"
        self.client2server_socket.sendto(message.encode('utf-8'), (self.SERVER_IP, self.SERVER_PORT))

    def deregister(self):
        self.RQ += 1
        message = f"DE-REGISTER {self.RQ} {self.username}"
        self.client2server_socket.sendto(message.encode('utf-8'), (self.SERVER_IP, self.SERVER_PORT))

    def update_contact(self):
        self.RQ += 1
        new_ip = self.client2client_socket.gethostbyname(self.HOST_NAME)
        new_port = int(input("What's your new port number? "))
        update_message = f"UPDATE-CONTACT {self.RQ} {self.username} {new_ip} {new_port}"

        self.client2server_socket.sendto(update_message.encode('utf-8'), (self.SERVER_IP, self.SERVER_PORT))
        self.SERVER_IP = new_ip
        self.SERVER_PORT = new_port
        self.client2client_socket.bind((self.CLIENT_IP, self.CLIENT_PORT))
        self.tcp.bind((self.CLIENT_IP, self.CLIENT_PORT))

    def request_info(self):
        self.RQ += 1
        message = f"REQUEST-INFO"
        self.client2server_socket.sendto(message.encode('utf-8'), (self.SERVER_IP, self.SERVER_PORT))

    def publish(self): # upload file to server if you want others to see it
        self.RQ += 1
        filename = input("What is the name of the file you would like to upload to server: ")
        message = f"PUBLISH {self.RQ} {self.username} {filename}"
        self.client2server_socket.sendto(message.encode('utf-8'), (self.SERVER_IP, self.SERVER_PORT))

    def remove(self):
        self.RQ += 1
        filename = input("Which file would you like to delete?: ")
        message = f"REMOVE {self.RQ} {self.username} {filename}"
        self.client2server_socket.sendto(message.encode('utf-8'), (self.SERVER_IP, self.SERVER_PORT))

    def filetransfer(self): # ask server if file exists
        self.RQ += 1
        filename = input("Which file would you like to check from server?: ")
        message = f"CHECKFILE {self.username} {filename}"
        self.client2server_socket.sendto(message.encode('utf-8'), (self.SERVER_IP, self.SERVER_PORT))

    def client2client_UDP(self): # make a connection to client, should have received IP and port from server if it exists
        ip = input("What is the IP of client that holds the file: ")
        port = int(input("What is the port of the client that holds the file: "))
        filename = input(f"What is the filename: ")
        message = f"CONNECT {filename}" # creates message to send to client
        self.client2server_socket.sendto(message.encode('utf-8'), (ip, port))

    def client_send(self): # send stuff to server or client
        while True:
            message = input("").strip()
            if message == "REGISTER":
                self.register()
            elif message == "DE-REGISTER":
                self.deregister()
            elif message.startswith("UPDATE-CONTACT"):
                self.update_contact()
            elif message.startswith("REQUEST-INFO"):
                self.request_info()
            elif message == "PUBLISH": # send command to upload file to server
                self.publish()
            elif message == "REMOVE": # delete file if exists
                self.remove()
            elif message == "CHECKFILE": # send command to check which file you want to download if it exists
                self.filetransfer()
            elif message == "CLIENTCONNECT":  # this is for client2client command only, server will get it too
                self.client2client_UDP()

    def client_receive(self): # receive messages from server
        while True:
            try:
                data, address = self.client2server_socket.recvfrom(BUFFER_SIZE)
                message = data.decode('utf-8')
                print(message)
            except Exception as e:
                print(f'Error in receiving message: {e}')
                self.client2server_socket.close()
                break

    def start_receiver(self, IP, port, filename): # client that will receive file from sender
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp:
            try:
                timeout = 5
                tcp.settimeout(timeout)
                print(f"Attemping to TCP connect to {IP}:{port} now.")
                tcp.connect((IP, port))
                with open(filename, 'w') as file: # write into file
                    print(f"Downloading file: {filename}")
                    while True:
                        data, address = tcp.recv(BUFFER_SIZE)
                        if not data:
                            break
                        file.write(data.decode('utf-8'))
                    print(f"Finished downloading file {filename}.")
            except socket.timeout:
                print(f"Connection timed out on {IP}:{port} after {timeout} seconds. Could not establish TCP.")
            except Exception as e:
                print(f"Error occured in start_receiver: {e}")

            tcp.close()  # close tcp connection

    def start_sender(self, address, filename): # client that will send file to receiver
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp:
            try:
                tcp.bind(address)
                tcp.listen(1)
                connection, client_address = tcp.accept()
                print(f"Connection established with {client_address}")
                with open(filename, 'r') as file:
                    print(f"Sending {filename} now.")
                    while True:
                        char = file.read(BUFFER_SIZE)
                        if not char:
                            break
                        connection.sendall(char.encode('utf-8'), client_address)
            except socket.error as e:
                print(f"Error occured in start_sender: {e}")
            tcp.close()

Client = Client()

