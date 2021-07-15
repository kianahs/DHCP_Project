import socket, sys
import Packet
import generateMac
import struct
import binascii
import time
MAX_BYTES = 1024

serverPort = 67
clientPort = 68
TIMEOUT = 10
Lease_time = 30
initial_interval = 10
backOff_cutOff = 120
received_ip = None
lease_time_start = 0

class DHCP_client(object):

    def client(self):

        global received_ip
        global lease_time_start
        global Lease_time

        print("[CLIENT]: DHCP client is starting...\n")
        dest = ('<broadcast>', serverPort)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.bind(('0.0.0.0', clientPort))
        self.start_communicate(s, dest)

    def start_communicate(self, s, dest):
        global received_ip
        global lease_time_start
        global Lease_time
        global TIMEOUT

        print("[CLIENT]: Send DHCP discovery.")
        dhcp_discovery = DHCP_client.build_discover(self)
        s.sendto(dhcp_discovery, dest)
        dhcp_request = b''
        dhcp_offer = b''
        flag = True

        while flag:

            dhcp_offer, address = s.recvfrom(MAX_BYTES)

            if dhcp_offer[4:8] == dhcp_discovery[4:8] and dhcp_offer[230:233] == b'\x35\x01\x02':
                # print(len(dhcp_offer))
                # print(dhcp_offer[230:233])
                # print(b'\x35\x01\x02')
                print("[CLIENT]: Receive DHCP offer.")
                offered_ip = socket.inet_ntoa(dhcp_offer[16:20])
                print("OFFERED IP --> ", offered_ip)

                dhcp_request = DHCP_client.build_request(self, dhcp_offer)
                s.sendto(dhcp_request, dest)
                s.sendto(dhcp_request, dest)
                print("[CLIENT]: Send DHCP request.")
                flag = False

        timeOut_start = time.time()
        # print(timeOut_start)
        # time.sleep(8)
        # print(time.time())
        while not flag and time.time()-timeOut_start <= TIMEOUT:

            dhcp_ack, address = s.recvfrom(MAX_BYTES)

            if dhcp_ack[4:8] == dhcp_discovery[4:8] and dhcp_ack[230:233] == b'\x35\x01\x05':
                lease_time_start = time.time()

                print("[CLIENT]: Receive DHCP pack.\n")
                received_ip = socket.inet_ntoa(dhcp_ack[16:20])
                print("RECEIVED IP --> ", received_ip)
                flag = True

            while time.time() - lease_time_start <= Lease_time:
                pass

            received_ip = None

        if not flag:
            #means time out
            print("Timeout start again")
            self.start_communicate(s, dest)





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
        mac = generateMac.getRandomMac()
        print(type(mac))
        print(mac)
        macbytes = binascii.unhexlify(mac)
        return macbytes

if __name__ == '__main__':
    dhcp_client = DHCP_client()
    dhcp_client.client()

    while input() != "1":
        pass

