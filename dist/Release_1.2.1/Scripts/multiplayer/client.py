# client.py
import socket
import threading
import json
import time

SIGNALING_SERVER_IP = '198.211.117.27'
SIGNALING_SERVER_PORT = 5555

# Create a UDP socket and bind to any available port
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', 0))  # Bind to a random available port
local_udp_ip, local_udp_port = sock.getsockname()

def listen_for_data():
    while True:
        try:
            data, addr = sock.recvfrom(4096)
            try:
                message = json.loads(data.decode())
                print(f"[FROM {addr}] {message['content']}")
            except json.JSONDecodeError:
                print(f"[FROM {addr}] Raw: {data}")
        except Exception as e:
            print(f"[!] Error receiving data: {e}")

def main():
    # Connect to signaling server over TCP
    tcp_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_conn.connect((SIGNALING_SERVER_IP, SIGNALING_SERVER_PORT))

    # Send UDP port to the signaling server
    tcp_conn.send(f"{local_udp_port}".encode())

    # Receive peer info from server
    peer_info = tcp_conn.recv(1024).decode()
    print(f"[+] Got peer info: {peer_info}")
    peer_ip, peer_port = peer_info.split(":")
    peer_port = int(peer_port)

    tcp_conn.close()

    # NAT punching: send dummy packets to peer to open NAT path
    print(f"[>] Punching to {peer_ip}:{peer_port}")
    for i in range(10):
        sock.sendto(b"punch", (peer_ip, peer_port))
        time.sleep(0.1)

    # Start listener thread
    threading.Thread(target=listen_for_data, daemon=True).start()

    # Main loop to send chat messages
    print("[*] Ready. Type messages below:")
    while True:
        message = input("> ")
        if not message.strip():
            continue
        data = {
            "type": "chat",
            "content": message
        }
        sock.sendto(json.dumps(data).encode(), (peer_ip, peer_port))

if __name__ == "__main__":
    main()
