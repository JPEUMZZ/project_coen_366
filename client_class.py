import socket
import sys
import threading
import os

BUFFER_SIZE = 1024

class Client(threading.Thread):
    def __init__(self):
        super(Client, self).__init__()
        self.client2server_socket = socket
        self.client2client_socket = socket

        self.HOST_NAME = socket.gethostname()
        self.CLIENT_IP = self.client2server_socket.gethostbyname(self.HOST_NAME)
        self.CLIENT_PORT = int(4000)

        self.SERVER_IP = input("Which Server IP would you like to connect to: ")
        self.SERVER_PORT = int(input("What is the server port: "))
        self.username = input(f"Enter you name: ").strip()

        try:
            self.client2server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except socket.error as msg:
            print(f"Error creating socket. Code {str(msg[0])}: {str(msg[1])}")
            sys.exit()

        self.register()
        self.listen()

    def listen(self):
        send_thread = threading.Thread(target=self.client_send)
        send_thread.start()

        receive_thread = threading.Thread(target=self.client_receive)
        receive_thread.start()

        clientrecv_udp_thread = threading.Thread(target=self.ClientFileProvider_udp) # as a seperate thread always listening
        clientrecv_udp_thread.start()

    def ClientFileProvider_udp(self): # the client that wants to receive file, will initially make request
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.bind((self.CLIENT_IP, self.SERVER_PORT))
            while True: # want to continuously listen for anything from other clients
                data, address = s.recvfrom(BUFFER_SIZE)
                clientrecv_thread = threading.Thread(target=self.ClientFileProvider_Thread, args=(s, data, address))
                clientrecv_thread.start()
            socket.close()

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
        message = f"REGISTER {self.username} {self.CLIENT_IP} {self.SERVER_PORT}"
        self.client2server_socket.sendto(message.encode('utf-8'), (self.SERVER_IP, self.SERVER_PORT))

    def deregister(self):
        message = f"DEREGISTER {self.username}"
        self.client2server_socket.sendto(message.encode('utf-8'), (self.SERVER_IP, self.SERVER_PORT))

    def uploadfile(self): # upload file to server if you want others to see it
        filename = input("What is the name of the file you would like to upload to server: ")
        message = f"UPLOADFILE {self.username} {filename}"
        self.client2server_socket.sendto(message.encode('utf-8'), (self.SERVER_IP, self.SERVER_PORT))

    def filetransfer(self): # ask server if file exists
        filename = input("Which file would you like to check from server?: ")
        message = f"CHECKFILE {self.username} {filename}"
        self.client2server_socket.sendto(message.encode('utf-8'), (self.SERVER_IP, self.SERVER_PORT))

    def client2client_UDP(self): # make a connection to client, should have received IP and port from server if it exists
        ip = input("What is the IP of client that holds the file: ")
        port = input("What is the port of the client that holds the file: ")
        filename = input(f"What is the filename: ")

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp:
            message = f"CONNECT {filename}" # creates message to send to client
            udp.sendto(message.encode('utf-8'), (ip, int(port))) # sends connect command to client
            data, address = udp.recvfrom(BUFFER_SIZE) # waits for accept or reject
            if data.decode('utf-8') == "ACCEPT": # if accept then close UDP
                udp.close()
                print(f"{address} has accepted connection. Attempting to establish TCP.")
                self.start_receiver(ip, port, filename) # start TCP connection
            else:
                if data.decode('utf-8') == "REJECT":
                    print(f"Rejected connection from {ip}:{port}. Could not receive file.")
                    udp.close()

    def client_send(self): # send stuff to server or client
        while True:
            message = input("").strip()
            if message == "REGISTER":
                self.register()
            elif message == "DEREGISTER":
                self.deregister()
            elif message == "UPLOADFILE": # send command to upload file to server
                self.uploadfile()
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
                with open(filename, 'wb') as file: # write into file
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
                with open(filename, 'rb') as file:
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

