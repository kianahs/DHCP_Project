import socket
import threading
from uuid import getnode as get_mac
import struct
import Packet
import random
import socket
import struct
import json


MAX_BYTES = 1024

serverPort = 67
clientPort = 68

def ip2int(addr):
    return struct.unpack("!I", socket.inet_aton(addr))[0]

def offer_ip():

    f = open('configs.json', )
    data = json.load(f)
    start = data['range']['from']
    stop = data['range']['to']
    f.close()
    start_num = ip2int(start)
    stop_num = ip2int(stop)
    random_ip = socket.inet_ntoa(struct.pack('>I', random.randint(start_num, stop_num)))
    print("offered ip is:", random_ip)
    return random_ip, "127.0.0.1"

class DHCP_server(object):

    def server(self):

        print("[SERVER]: SERVER STARTS")

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.bind(('', serverPort))
        # print(s.getsockname())
        dest = ('255.255.255.255', clientPort)
        clients_transactions = []

        while 1:
            try:
                print("[SERVER]: Wait for DHCP discovery.")
                discovery, address = s.recvfrom(MAX_BYTES)
                if discovery[4:8] not in clients_transactions and discovery[240:243] == b'\x35\x01\x01':

                    print("[SERVER]: Receive DHCP discovery from ", address)
                    clients_transactions.append(discovery[4:8])

                    t = threading.Thread(target=self.talk, args=(address, dest, s, discovery, discovery[4:8]))
                    t.start()

            except:
                raise

    def talk(self, address, dest, s, discovery, transactionID):

        dhcp_offer = DHCP_server.build_offer(self, discovery)
        print("[SERVER]: Send DHCP offer")
        s.sendto(dhcp_offer, dest)

        while 1:
            try:
                # print("transaction id",socket.inet_ntoa(transactionID))
                # print("transaction id", socket.inet_ntoa(dhcp_offer[4:8]))
                print("[SERVER]: Wait DHCP request.")
                dhcp_request, address = s.recvfrom(MAX_BYTES)
                print(len(dhcp_request))
                print("11111")
                print(transactionID)
                print(dhcp_request[4:8])
                print(transactionID)

                if dhcp_request[4:8] == transactionID and dhcp_request != dhcp_offer:

                    print("[SERVER]: Receive DHCP request.")
                    # print(data)
                    dhcp_ack = DHCP_server.build_ack(self, dhcp_request)
                    s.sendto(dhcp_ack, dest)
                    print("[SERVER]: Send DHCP ack.\n")
                    break
            except :
                raise




    def build_offer(self,discovery):

        packet = Packet.DHCPOffer(discovery)
        offered_ip, next_server = offer_ip()
        package = packet.buildPacket(offered_ip, next_server)
        return package

    def build_ack(self,dhcp_request):

        packet = Packet.DHCPAcknowledgement(dhcp_request)
        package = packet.buildPacket()
        return package

    def getMacInBytes(self):

        mac = str(hex(get_mac()))
        mac = mac[2:]
        while len(mac) < 12:
            mac = '0' + mac
        macb = b''
        for i in range(0, 12, 2):
            m = int(mac[i:i + 2], 16)
            macb += struct.pack('!B', m)
        return macb

if __name__ == '__main__':
    dhcp_server = DHCP_server()
    dhcp_server.server()