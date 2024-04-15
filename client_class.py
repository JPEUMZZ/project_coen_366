import socket
import sys
import threading

BUFFER_SIZE = 1024

class Client(threading.Thread):
    def __init__(self):
        super(Client, self).__init__()
        self.client2server_socket = socket
        self.client2client_socket = socket
        self.HOST_NAME = socket.gethostname()
        self.CLIENT_IP = self.client2server_socket.gethostbyname(self.HOST_NAME)
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

        #transfer_thread = threading.Thread(target=self.request_file_from_client())
        #transfer_thread.start()

        #sender_thread = threading.Thread(target=self.start_sender)
        #sender_thread.start()


    def register(self):
        message = f"REGISTER {self.username} {self.CLIENT_IP} {self.SERVER_PORT}"
        self.client2server_socket.sendto(message.encode('utf-8'), (self.SERVER_IP, self.SERVER_PORT))

    def deregister(self):
        message = f"DEREGISTER {self.username}"
        self.client2server_socket.sendto(message.encode('utf-8'), (self.SERVER_IP, self.SERVER_PORT))

    def uploadfile(self):
        filename = input("What is the name of the file you would like to upload to server: ")
        message = f"UPLOADFILE {self.username} {filename}"
        self.client2server_socket.sendto(message.encode('utf-8'), (self.SERVER_IP, self.SERVER_PORT))

    def filetransfer(self):
        filename = input("Which file would you like to download?: ")
        message = f"DOWNLOADFILE {self.username} {filename}"
        self.client2server_socket.sendto(message.encode('utf-8'), (self.SERVER_IP, self.SERVER_PORT))

    def client_send(self): # send stuff to server or client
        while True:
            message = input("").strip()
            if message == "REGISTER":
                self.register()
            elif message == "DEREGISTER":
                self.deregister()
            elif message == "UPLOADFILE":
                self.uploadfile()
            elif message == "DOWNLOADFILE":
                self.filetransfer()
            elif message == "CLIENTCONNECT":
                self.request_file_from_client()

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

    def receive_file(self, tcp_socket, filename):
        with open(filename, 'wb') as file:
            while True:
                data = tcp_socket.recv(BUFFER_SIZE)
                if not data:
                    break
                file.write(data)
        tcp_socket.close()

    def request_file_from_client(self):
        ip = input("What is the IP of client that holds the file: ")
        port = input("What is the port of the client that holds the file: ")
        filename = input(f"{ip}:{port} -> Filename: ")

        client_thread = threading.Thread(target=self.start_receiver(ip, port, filename))
        client_thread.start()

    def start_receiver(self, IP, port, filename):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                timeout = 5
                print(f"Listening for ACK from {IP}{port}.")
                s.settimeout(timeout)
                s.connect((IP, port))
                s.send(filename)
                self.receive_file(s, filename)
            except s.timeout:
                print(f"Connection timed out on {IP}:{port} after {timeout} seconds.")
            except Exception as e:
                print(f"Error occured: {e}")

    def start_sender(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                while True:
                    connection, client_address = s.accept()
                    print(f"Connection established with {client_address}")
            except Exception as e:
                print(f"Error occured: {e}")
        s.close()

Client = Client()

