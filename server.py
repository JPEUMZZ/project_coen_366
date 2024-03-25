
import socket
import threading

# Server details
SERVER_IP = socket.gethostbyname(socket.gethostname())
SERVER_PORT = 3000
BUFFER_SIZE = 1024

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((SERVER_IP, SERVER_PORT))

# Dictionary to store user data: {username: (IP, Port)}
users = {}

# Handle client messages
def handle_client_message(client_socket, client_address):
    while True:
        message, client_address = client_socket.recvfrom(BUFFER_SIZE)
        message = message.decode('utf-8')
        print(f"Message from {client_address}: {message}")
        
        if message.startswith("REGISTER"):
            _, username, ip, port = message.split()
            if username in users:
                response = f"REGISTRATION DENIED for {username}. Reason: Username already in use."
            else:
                users[username] = (ip, port)
                response = f"REGISTRATION CONFIRMED for {username}."
            client_socket.sendto(response.encode('utf-8'), client_address)
        
        elif message.startswith("DEREGISTER"):
            _, username = message.split()
            if username in users:
                del users[username]
                response = f"{username} deregistered successfully."
            else:
                response = f"{username} is not registered."
            client_socket.sendto(response.encode('utf-8'), client_address)

# Create UDP server socket


print(f"UDP server listening on {SERVER_IP}:{SERVER_PORT}")

while True:
    message, client_address = server_socket.recvfrom(BUFFER_SIZE)
    threading.Thread(target=handle_client_message, args=(server_socket, client_address)).start()