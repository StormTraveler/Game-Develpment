# signaling_server.py
import socket
import threading

clients = []

def handle_client(conn, addr):
    print(f"New client: {addr}")
    clients.append((conn, addr))
    if len(clients) == 2:
        # Once 2 clients are connected, share addresses
        (conn1, addr1), (conn2, addr2) = clients
        conn1.send(f"{addr2[0]}:{addr2[1]}".encode())
        conn2.send(f"{addr1[0]}:{addr1[1]}".encode())
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
