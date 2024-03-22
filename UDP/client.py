import socket
import os

# Constants
SERVER_IP = '127.0.0.1'  # Server IP address
SERVER_PORT = 12345
BUFFER_SIZE = 1024
TIMEOUT = 2  # Timeout in seconds

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.settimeout(TIMEOUT)

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
                if f.tell() > BUFFER_SIZE:
                    f.seek(-BUFFER_SIZE, os.SEEK_CUR)  # Only move back if not at the start of the file
                else:
                    print("Cannot resend - at the beginning of the file.")
                    break

def receive_file(filename):
    download_path = os.path.join("downloads", filename)  # Path in downloads folder
    client_socket.sendto(f"get {filename}".encode(), (SERVER_IP, SERVER_PORT))
    with open(download_path, 'wb') as f:
        while True:
            try:
                bytes_read, _ = client_socket.recvfrom(BUFFER_SIZE)
                if bytes_read == b'END':
                    break
                f.write(bytes_read)
                client_socket.sendto(b'ACK', (SERVER_IP, SERVER_PORT))
            except socket.timeout:
                print("Failed to receive file.")
                break

try:
    command = input("Enter command (put/get) and filename: ")
    cmd, filename = command.split()
except ValueError:
    print("Error: Please enter the command and filename separated by a space.")
else:
    if cmd == 'put':
        send_file(filename)
    elif cmd == 'get':
        receive_file(filename)
    else:
        print("Invalid command. Use 'put' or 'get'.")
