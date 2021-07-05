import threading
import socket
import logging

class server_DHCP():

    def __init__(self):
        print("SERVER : SERVER STARTS ......")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('127.0.0.1', 4242))
        self.clients_list = []

    def talkToClient(self, ip):
        print("SERVER : SENDING WELCOME ......")
        self.sock.sendto("SERVER : WELCOME".encode('utf-8'), ip)

    def listen_clients(self):
        while True:
            msg, client = self.sock.recvfrom(1024)
            msg = msg.decode('utf-8')
            print('SERVER : RECEIVING DATA FROM CLIENT :', client, msg)
            t = threading.Thread(target=self.talkToClient, args=(client,))
            t.start()

if __name__ == '__main__':
    s = server_DHCP()
    s.listen_clients()