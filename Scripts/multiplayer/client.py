# client.py
import socket
import threading
import json

SIGNALING_SERVER_IP = '198.211.117.27'
SIGNALING_SERVER_PORT = 5555

# Local UDP socket for punching
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', 0))  # Bind to random available port

def listen_for_data():
    while True:
        try:
            data, addr = sock.recvfrom(4096)
            message = json.loads(data.decode())
            print(f"Received from {addr}: {message}")
        except Exception as e:
            print(f"Error receiving: {e}")

def main():
    # Connect to signaling server
    tcp_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_conn.connect((SIGNALING_SERVER_IP, SIGNALING_SERVER_PORT))

    # Send our public IP/port (the server will automatically know from TCP connection)
    # Just wait for opponent info
    peer_info = tcp_conn.recv(1024).decode()
    print(f"Got peer info: {peer_info}")
    peer_ip, peer_port = peer_info.split(":")
    peer_port = int(peer_port)

    tcp_conn.close()

    # NAT punching: send dummy packet to peer
    print(f"Punching to {peer_ip}:{peer_port}")
    for _ in range(10):  # send multiple times just in case
        sock.sendto(b"punch", (peer_ip, peer_port))

    # Start thread to listen for real data
    threading.Thread(target=listen_for_data, daemon=True).start()

    # Now send JSON messages
    while True:
        message = input("Type message: ")
        data = {
            "type": "chat",
            "content": message
        }
        sock.sendto(json.dumps(data).encode(), (peer_ip, peer_port))

if __name__ == "__main__":
    main()
