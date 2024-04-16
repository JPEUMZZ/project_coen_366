import socket
import sys
import threading

BUFFER_SIZE = 1024

class Client(threading.Thread):
    def __init__(self):
        super(Client, self).__init__()
        self.client_socket = socket
        self.HOST_NAME = socket.gethostname()
        self.CLIENT_IP = self.client_socket.gethostbyname(self.HOST_NAME)
        self.SERVER_IP = input("Which Server IP would you like to connect to: ")
        self.SERVER_PORT = int(input("What is the server port: "))
        self.client_IP = input("What is your IP address? ")
        self.client_PORT = int(input("What is your port? "))
        self.username = input(f"Enter you name: ").strip()

        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
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

    def register(self):
        message = f"REGISTER {self.username} {self.client_IP} {self.client_PORT}"
        self.client_socket.sendto(message.encode('utf-8'), (self.SERVER_IP, self.SERVER_PORT))

    def deregister(self):
        message = f"DEREGISTER {self.username}"
        self.client_socket.sendto(message.encode('utf-8'), (self.SERVER_IP, self.SERVER_PORT))

    def update_contact(self):
        new_ip = input("What's your new IP address? ")
        new_port = input("What's your new port number? ")
        update_message = f"UPDATE-CONTACT {self.username} {new_ip} {new_port}"
        self.client_socket.sendto(update_message.encode('utf-8'), (self.SERVER_IP, self.SERVER_PORT))
        self.SERVER_IP = new_ip
        self.SERVER_PORT = new_port

    def request_info(self):
        message = f"REQUEST-INFO"
        self.client_socket.sendto(message.encode('utf-8'), (self.SERVER_IP, self.SERVER_PORT))

    def client_send(self):
        while True:
            message = input("").strip()
            if message == "REGISTER":
                self.register()
            elif message == "DEREGISTER":
                self.deregister()
            elif message.startswith("UPDATE-CONTACT"):
                self.update_contact()
            elif message.startswith("REQUEST-INFO"):
                self.request_info()

    def client_receive(self):
        while True:
            try:
                data, address = self.client_socket.recvfrom(BUFFER_SIZE)
                message = data.decode('utf-8')
                print(message)
            except Exception as e:
                print(f'Error in receiving message: {e}')
                self.client_socket.close()
                break


Client = Client()
