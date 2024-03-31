import socket

# Server details
SERVER_IP = socket.gethostbyname(socket.gethostname())  # Replace with your server's IP
SERVER_PORT = 3000
BUFFER_SIZE = 1024

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def register(username, ip, port):
    message = f"REGISTER {username} {ip} {port}"
    client_socket.sendto(message.encode('utf-8'), (SERVER_IP, SERVER_PORT))
    response, _ = client_socket.recvfrom(BUFFER_SIZE)
    print("Server response:", response.decode('utf-8'))

def deregister(username):
    message = f"DEREGISTER {username}"
    client_socket.sendto(message.encode('utf-8'), (SERVER_IP, SERVER_PORT))
    response, _ = client_socket.recvfrom(BUFFER_SIZE)
    print("Server response:", response.decode('utf-8'))

def main():
    while True:
        # Ask the user what they want to do
        action = input("Do you want to REGISTER or DEREGISTER? Type 'exit' to quit: ").strip().upper()
        if action == 'EXIT':
            print("Exiting...")
            break

        if action == "REGISTER":
            name = input("Enter your name: ").strip()
            ip = input("Enter your IP address: ").strip()
            udp_socket = input("Enter your UDP socket number: ").strip()
            register(name, ip, udp_socket)
        elif action == "DEREGISTER":
            name = input("Enter your name: ").strip()
            deregister(name)
        else:
            print("Invalid action. Please try again.")
            continue

    # Close the socket
    client_socket.close()

if __name__ == "__main__":
    main()
