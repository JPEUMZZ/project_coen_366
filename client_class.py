import socket
import sys
import threading
import os

BUFFER_SIZE = 1024

class Client(threading.Thread):
    class_counter= 3001
    lock = threading.Lock()
    def __init__(self):
        super(Client, self).__init__()
        self.HOST_NAME = socket.gethostname()
        self.CLIENT_IP = socket.gethostbyname(self.HOST_NAME)
        
        self.SERVER_IP = input("Which Server IP would you like to connect to: ")
        self.SERVER_PORT = int(input("What is the server port: "))
        self.username = input("Enter your name: ").strip()

        with Client.lock:
            self.CLIENT_PORT = Client.class_counter
            Client.class_counter += 1

        try:
            self.client2server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.client2client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except socket.error as msg:
            print(f"Error creating socket: {msg}")
            sys.exit()

        self.register()
        self.listen()



    def create_socket(self):
        self.client2client_socket.bind((self.SERVER_IP, self.PORT))
        while True:
            message, client_address = self.client2client_socket.recvfrom(BUFFER_SIZE)
            threading.Thread(target=self.listening, args=(message, client_address)).start()


            
   


    def listen(self):
        send_thread = threading.Thread(target=self.client_send)
        send_thread.start()

        receive_thread = threading.Thread(target=self.client_receive)
        receive_thread.start()

        # JUNIOR UNCOMMENT THIS, THE LINE BELOW IS SUPPOSE TO RECEIVE COMMAND FROM OTHER CLIENT FIRST AS UDP THEN TCP
        clientrecv_udp_thread = threading.Thread(target=self.create_socket())
        clientrecv_udp_thread.start()

    def clientreceive_udp(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            while True: # want to continuoulsy listen for anything from other clients
                data, address = s.recvfrom(BUFFER_SIZE)
                message = data.decode('utf-8')
                command, filename = message
                if command.startswith("CONNECT"): # if receive message from client as connect
                    try:
                        _, filename = data.decode('utf-8')
                        if os.path.exists(filename):
                            answer = input(f"File {filename} is being requested by {address}. "
                                           f"Do we send it? (ACCEPT/REJECT): ")
                            message = answer.upper().encode('utf-8')
                            if answer.upper() == "ACCEPT":
                                s.sendto(message, address)
                                s.close()
                                thread = threading.Thread(self.start_sender(address, filename))
                                thread.start()

                        message = f"REJECT" # auto reject if file doesnt exist
                        s.sendto(message.encode('utf-8'), address)
                        s.close()
                        break

                    except Exception as e:
                        print(f'Error in receiving message: {e}')
                        s.close()
                        break

    def register(self):
        message = f"REGISTER {self.username} {self.CLIENT_IP} {self.CLIENT_PORT}"
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

    def client2clientUDP(self): # make a connection to client, should have received IP and port from server if it exists
        ip = input("What is the IP of client that holds the file: ")
        port = int(input("What is the port of the client that holds the file: "))
        message = "conection: "
        self.client2client_socket.sendto(message.encode('utf-8'), (ip, port))
        
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
                self.client2clientUDP()
            

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
                tcp.connect((IP, port))
                self.receive_file(tcp, filename)
            except tcp.timeout:
                print(f"Connection timed out on {IP}:{port} after {timeout} seconds. Could not establish TCP.")
            except Exception as e:
                print(f"Error occured in start_receiver: {e}")

    def start_sender(self, address, filename): # client that will send file to receiver
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp:
            try:
                tcp.bind(address)
                tcp.listen(1)
                connection, client_address = tcp.accept()
                print(f"Connection established with {client_address}")

                with open(filename, 'wb') as file:
                    while True:
                        char = file.read(1)
                        if not char:
                            break
                        tcp.sendto(char.encode('utf-8'), client_address)
            except Exception as e:
                print(f"Error occured in start_sender: {e}")
        tcp.close()

    def receive_file(self, tcp_socket, filename): # receive character from sender client
        with open(filename, 'rb') as file:
            while True:
                data = tcp_socket.recv(BUFFER_SIZE)
                if not data:
                    break
                file.write(data)
            print(f"Finished downloading file {filename}.")
        tcp_socket.close() # close tcp connection

    def update_contact(self):
        new_ip = input("What's your new IP address? ")
        new_port = input("What's your new port number? ")
        update_message = f"UPDATE-CONTACT {self.username} {new_ip} {new_port}"
        self.client2server_socket.sendto(update_message.encode('utf-8'), (self.SERVER_IP, self.SERVER_PORT))
        self.SERVER_IP = new_ip
        self.SERVER_PORT = new_port

    def listening(self, message, client_address):
        msg = message.decode('utf-8')
        print(f"Message incoming from {client_address}")
        # registration
        if msg.startswith("conection"):
            response = " accepte"
            self.client2client_socket.sendto(response.encode('utf-8'), client_address)

Client = Client()