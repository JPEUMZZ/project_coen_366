
import socket
import threading


SERVER_IP = socket.gethostbyname(socket.gethostname())
SERVER_PORT = 3000
BUFFER_SIZE = 1024

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((SERVER_IP, SERVER_PORT))

users = {}

def send_notification(message):
    for username, user_details in users.items():
        server_socket.sendto(message.encode('utf-8'), user_details["address"])


def handle_client_message(message, client_address):
    message = message.decode('utf-8')
    print(f"Message from {client_address}: {message}")
    
    if message.startswith("REGISTER"):
        parts = message.split()
        if len(parts) == 4:
            _, username, ip, port = parts
            if username in users:
                response = f"REGISTRATION DENIED for {username}. Reason: Username already in use."
            else:
                users[username] = {"IP":ip , "port":port, "address":client_address}
                response = f"REGISTRATION CONFIRMED for {username}."
                notification = f"{username} has registered."
                send_notification(notification)
        else:
            response = "Invalid registration message format."
        server_socket.sendto(response.encode('utf-8'), client_address)
    
    elif message.startswith("DEREGISTER"):
        _, username = message.split()
        if username in users:
            del users[username]
            response = f"{username} deregistered successfully."
            notification = f"{username} has deregistered."
            send_notification(notification)
        else:
            response = f"{username} is not registered."
        server_socket.sendto(response.encode('utf-8'), client_address)

print(f"UDP server listening on {SERVER_IP}:{SERVER_PORT}")

while True:
    message, client_address = server_socket.recvfrom(BUFFER_SIZE)
    threading.Thread(target=handle_client_message, args=(message, client_address)).start()
