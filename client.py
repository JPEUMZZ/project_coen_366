# import threading
# import socket
# port = 5050
# host = socket.gethostbyname(socket.gethostname())
# alias = input('Choose an alias >>> ')
# client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# client.connect((host, port))


# def client_receive():
#     while True:
#         try:
#             message = client.recv(1024).decode('utf-8')
#             if message == "alias?":
#                 client.send(alias.encode('utf-8'))
#             else:
#                 print(message)
#         except:
#             print('Error!')
#             client.close()
#             break


# def client_send():
#     while True:
#         message = f'{alias}: {input("")}'
#         client.send(message.encode('utf-8'))


# receive_thread = threading.Thread(target=client_receive)
# receive_thread.start()

# send_thread = threading.Thread(target=client_send)
# send_thread.start()

import socket

# Server details
SERVER_IP = socket.gethostbyname(socket.gethostname())
SERVER_PORT = 3000
BUFFER_SIZE = 1024

# Client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Function to communicate with the server
def communicate_with_server(message):
    client_socket.sendto(message.encode('utf-8'), (SERVER_IP, SERVER_PORT))
    response, _ = client_socket.recvfrom(BUFFER_SIZE)
    print("Server response:", response.decode('utf-8'))

def main():
    while True:
        # Ask the user what they want to do
        action = input("Do you want to REGISTER or DEREGISTER? Type 'exit' to quit. ").strip().upper()
        if action == 'EXIT':
            print("Exiting...")
            break

        if action == "REGISTER":
            name = input("Enter your name: ").strip()
            ip = input("Enter your IP address: ").strip()
            udp_socket = input("Enter your UDP socket number: ").strip()
            message = f"REGISTER {name} {ip} {udp_socket}"
        elif action == "DEREGISTER":
            name = input("Enter your name: ").strip()
            message = f"DEREGISTER {name}"
        else:
            print("Invalid action. Please try again.")
            continue

        # Send message to the server
        communicate_with_server(message)

    # Close the socket
    client_socket.close()

if __name__ == "__main__":
    main()











# import socket

# HEADER = 64
# PORT = 5050
# SERVER = socket.gethostbyname(socket.gethostname())
# ADDR = (SERVER, PORT)
# FORMAT = 'utf-8'
# DISCONNECT_MESSAGE = "!DISCONNECT"

# client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# client.connect(ADDR)

# def send(msg):
    
#     message = msg.encode(FORMAT)
#     msg_length = len(message)
#     send_length = str(msg_length).encode(FORMAT)
#     send_length += b' ' * (HEADER - len(send_length))
#     client.send(send_length)
#     client.send(message)
#     print(client.recv(2048).decode(FORMAT))

# send("Hello World!")
# input() 
# send("project")
# input()
# send("Coen 366")
# input()
# send(DISCONNECT_MESSAGE)