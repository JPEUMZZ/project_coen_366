import socket
import threading

SERVER_IP = socket.gethostbyname(socket.gethostname())
SERVER_PORT = 3000
BUFFER_SIZE = 1024
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


name = input("Enter your name: ").strip()
ip = input("Enter your IP address: ").strip()
udp_socket = input("Enter your UDP socket number: ").strip()

def register(username, ip, port):
    message = f"REGISTER {username} {ip} {port}"
    client_socket.sendto(message.encode('utf-8'), (SERVER_IP, SERVER_PORT))
   

def deregister(username):
    message = f"DEREGISTER {username}"
    client_socket.sendto(message.encode('utf-8'), (SERVER_IP, SERVER_PORT))
   

def client_send():
    while True:
        message = input("").strip().upper()
        if message == "DEREGISTER":
            deregister(name)


def client_receive():
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            print(message)
        except:
            print('Error!')
            client_socket.close()
            break



register(name, ip, udp_socket)

receive_thread = threading.Thread(target=client_receive)
receive_thread.start()

send_thread = threading.Thread(target=client_send)
send_thread.start()
    
