# signaling_server.py
import socket
import threading

clients = []

def handle_client(conn, addr):
    print(f"New client: {addr}")
    udp_port = int(conn.recv(1024).decode())  # Receive UDP port
    client_info = (addr[0], udp_port)  # Use IP from TCP + UDP port from client
    clients.append((conn, client_info))

    if len(clients) == 2:
        (_, client1), (_, client2) = clients
        clients[0][0].send(f"{client2[0]}:{client2[1]}".encode())
        clients[1][0].send(f"{client1[0]}:{client1[1]}".encode())
        clients.clear()


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 5555))
    server.listen(5)
    print("Signaling server listening on port 5555")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == "__main__":
    main()
