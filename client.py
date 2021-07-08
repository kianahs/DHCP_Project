import socket, sys
import Packet
from uuid import getnode as get_mac
import struct

MAX_BYTES = 1024

serverPort = 67
clientPort = 68


class DHCP_client(object):

    def client(self):

        print("[CLIENT]: DHCP client is starting...\n")
        dest = ('<broadcast>', serverPort)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.bind(('0.0.0.0', clientPort))

        print("[CLIENT]: Send DHCP discovery.")
        dhcp_discovery = DHCP_client.build_discover(self)
        s.sendto(dhcp_discovery, dest)
        dhcp_request = b''
        dhcp_offer = b''
        flag = True

        while flag:

            dhcp_offer, address = s.recvfrom(MAX_BYTES)
            if dhcp_offer[4:8] == dhcp_discovery[4:8] and dhcp_offer != dhcp_discovery:
                print("[CLIENT]: Receive DHCP offer.")
                offered_ip = socket.inet_ntoa(dhcp_offer[16:20])
                print("OFFERED IP --> ", offered_ip)

                dhcp_request = DHCP_client.build_request(self, dhcp_offer)
                print(socket.inet_ntoa(dhcp_request[4:8]))
                print(socket.inet_ntoa(dhcp_offer[4:8]))
                print(socket.inet_ntoa(dhcp_discovery[4:8]))
                print("request size {} discovery size {} offer size {}".format(len(dhcp_request),len(dhcp_discovery), len(dhcp_offer)))
                s.sendto(dhcp_request, dest)
                s.sendto(dhcp_request, dest)
                print("[CLIENT]: Send DHCP request.")
                flag = False


        while not flag:

            dhcp_ack, address = s.recvfrom(MAX_BYTES)

            if dhcp_ack[4:8] == dhcp_discovery[4:8] and dhcp_ack != dhcp_request and dhcp_ack != dhcp_offer and dhcp_ack != dhcp_discovery:

                print("[CLIENT]: Receive DHCP pack.\n")
                received_ip = socket.inet_ntoa(dhcp_ack[16:20])
                print("RECEIVED IP --> ", received_ip )
                flag = True

        # print(data)
        # print(data)

    def build_discover(self):
        self.mac = self.getMacInBytes()
        self.discoverPacket = Packet.DHCPDiscover()
        package = self.discoverPacket.buildPacket(self.mac)

        return package

    def build_request(self, dhcp_offer):

        requestPacket = Packet.DHCPRequest(dhcp_offer)
        package = requestPacket.buildPacket()
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
    dhcp_client = DHCP_client()
    dhcp_client.client()

    while input() != "1":
        pass

