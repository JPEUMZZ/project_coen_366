import socket
import os

# Constants
UPLOAD_FOLDER = "uploads"
DOWNLOAD_FOLDER_DESTINATION = "downloads"
BUFFER_SIZE = 1024
PORT = 12345

# Create socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('', PORT))

def receive_file(filename):
    with open(os.path.join(UPLOAD_FOLDER, filename), 'wb') as f:
        while True:
            bytes_read, client_addr = server_socket.recvfrom(BUFFER_SIZE)
            if not bytes_read:
                break
            f.write(bytes_read)

def send_file(filename):
    filepath = os.path.join("to_upload", filename)  # Path in to_upload folder
    if not os.path.isfile(filepath):
        print(f"Error: The file '{filepath}' does not exist.")
        return

    with open(filepath, 'rb') as f:
        client_socket.sendto(f"put {os.path.basename(filename)}".encode(), (SERVER_IP, SERVER_PORT))
        while True:
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                client_socket.sendto(b'END', (SERVER_IP, SERVER_PORT))
                break
            client_socket.sendto(bytes_read, (SERVER_IP, SERVER_PORT))
            try:
                _, _ = client_socket.recvfrom(BUFFER_SIZE)  # Wait for ACK
            except socket.timeout:
                print("Timeout, resending packet")
                current_position = f.tell()  # Get the current position in the file
                if current_position >= BUFFER_SIZE:
                    f.seek(-BUFFER_SIZE, os.SEEK_CUR)  # Move back only if not at the start


print(f"Server listening on port {PORT}")
while True:
    msg, client_addr = server_socket.recvfrom(BUFFER_SIZE)
    command, filename = msg.decode().split()
    if command == 'put':
        receive_file(filename)
    elif command == 'get':
        send_file(filename, client_addr)
