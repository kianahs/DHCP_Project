import socket
import threading
import generateMac
import struct
import Packet
import random
import socket
import struct
import json
import time

MAX_BYTES = 1024

serverPort = 67
clientPort = 68
mac_ip = {}
ip_pool = []
reservation_list = {}
black_list = []
acked = []
lease_time = 0
time_starts = {} # mac-time

def mcbytes_to_str(macbytes):
   mac = "%x:%x:%x:%x:%x:%x" % struct.unpack("BBBBBB", macbytes)
   return mac.replace(':', '')



def ip2int(addr):
    return struct.unpack("!I", socket.inet_aton(addr))[0]


def offer_ip(mac):
    global reservation_list
    global black_list
    global mac_ip

    read_Json()

    if mac in mac_ip.keys():
        print("mac already has ip")
        return mac_ip[mac], "127.0.0.1"

    if mac in reservation_list.keys():
        print("mac address is in reservation list")
        return None, "127.0.0.1"

    if mac in black_list:
        print("mac address is in black list")
        return None, "127.0.0.1"


    global ip_pool
    # print("ip pool lenghth",len(ip_pool))
    index = random.randint(0, (len(ip_pool) - 2))
    random_ip = ip_pool[index ]


    print("offered ip is:", random_ip)
    return random_ip, "127.0.0.1"


def read_Json():

    global reservation_list
    global black_list

    f = open('configs.json', )
    data = json.load(f)
    pool_mode = data['pool_mode']
    start = ''
    stop = ''

    reservation_list = data['reservation_list']
    # print(type(reservation_list))
    black_list = data['black_list']
    # print(type(black_list))
    global lease_time
    lease_time = data['lease_time']

    if pool_mode == 'range':
        start = data['range']['from']
        stop = data['range']['to']
    elif pool_mode == 'subnet':
        start = data['subnet']['ip_block']
        stop = data['subnet']['subnet_mask']

    f.close()
    start_num = ip2int(start)
    stop_num = ip2int(stop)

    global ip_pool

    for i in range(100):

        random_ip = socket.inet_ntoa(struct.pack('>I', random.randint(start_num, stop_num)))
        ip_pool.append(random_ip)

    ip_pool = list(dict.fromkeys(ip_pool))


def get_key(val, my_dict):
    for key, value in my_dict.items():
         if val == value:
             return key

class DHCP_server(object):

    def server(self):

        print("[SERVER]: SERVER STARTS")
        global  acked
        global time_starts
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.bind(('', serverPort))
        # print(s.getsockname())
        dest = ('255.255.255.255', clientPort)
        clients_transactions = []

        while 1:
            try:
                print("SHOWING CLIENTS WITH IPS")
                self.show_clients()
                print("[SERVER]: Wait for DHCP discovery.")
                discovery, address = s.recvfrom(MAX_BYTES)
                if discovery[240:243] == b'\x35\x01\x01' :

                    if discovery[4:8] not in clients_transactions or discovery[4:8] not in acked:

                        print("[SERVER]: Receive DHCP discovery from ", address)
                        clients_transactions.append(discovery[4:8])

                        t = threading.Thread(target=self.talk, args=(address, dest, s, discovery, discovery[4:8]))
                        t.start()
                    else:

                        time_starts[mcbytes_to_str(discovery[28:34])] = time.time()

            except:
                raise

    def talk(self, address, dest, s, discovery, transactionID):

        dhcp_offer = DHCP_server.build_offer(self, discovery)

        if dhcp_offer == None:
            return

        print("[SERVER]: Send DHCP offer")
        s.sendto(dhcp_offer, dest)

        while 1:
            try:
                # print("transaction id",socket.inet_ntoa(transactionID))
                # print("transaction id", socket.inet_ntoa(dhcp_offer[4:8]))
                print("[SERVER]: Wait DHCP request.")
                dhcp_request, address = s.recvfrom(MAX_BYTES)
                # print(len(dhcp_request))
                # print("11111")
                # print(transactionID)
                # print(dhcp_request[4:8])
                # print(transactionID)

                if dhcp_request[4:8] == transactionID and dhcp_request != dhcp_offer:

                    print("[SERVER]: Receive DHCP request.")
                    # print(data)
                    # time.sleep(200)
                    dhcp_ack = DHCP_server.build_ack(self, dhcp_request)
                    s.sendto(dhcp_ack, dest)
                    global time_starts
                    start = time.time()
                    if dhcp_ack is not None:
                        print("[SERVER]: Send DHCP ack.\n")
                        time_starts[mcbytes_to_str(dhcp_ack[28:34])] = start
                        global lease_time
                        while time.time() - start <= lease_time:

                            pass

                        global ip_pool
                        global mac_ip
                        global acked
                        # global time_starts
                        # global time_starts
                        ip_pool.append(socket.inet_ntoa(dhcp_ack[16:20]))
                        # print(mac_ip)
                        del mac_ip[mcbytes_to_str(dhcp_ack[28:34])]
                        # del time_starts[mcbytes_to_str(dhcp_ack[28:34])]
                        acked.remove(dhcp_ack[4:8])



                    else:
                        print("[SERVER]: Send None DHCP ack.\n")
                    break
            except :
                raise


    def build_offer(self,discovery):

        mac = mcbytes_to_str(discovery[28:34])
        packet = Packet.DHCPOffer(discovery)
        offered_ip, next_server = offer_ip(mac)
        if offered_ip == None:
            return None
        global mac_ip
        while offered_ip == "192.168.1.0" and offered_ip not in mac_ip:
            print("[WARNING]: offered ip not usable generating new one!")
            offered_ip, next_server = offer_ip(mac)

        package = packet.buildPacket(offered_ip, next_server)
        return package

    def build_ack(self,dhcp_request):
        global mac_ip
        global ip_pool
        global acked
        mac_ip[mcbytes_to_str(dhcp_request[28:34])] = socket.inet_ntoa(dhcp_request[16:20])
        # print(mac_ip)

        if socket.inet_ntoa(dhcp_request[16:20]) in ip_pool:
            acked.append(dhcp_request[4:8])
            ip_pool.remove(socket.inet_ntoa(dhcp_request[16:20]))
            # print(ip_pool)
            packet = Packet.DHCPAcknowledgement(dhcp_request)
            package = packet.buildPacket()
            return package
        else:
            return None

    def reserve_ip_for_mac(self, ip, mac):

        global ip_pool
        ip_pool.remove(ip)
        global mac_ip
        mac_ip[mac] = ip

    def block_mac (self, mac):

        global black_list
        black_list.append(mac)

    def show_clients(self):
        global time_starts
        global mac_ip
        for mac in mac_ip.keys():
            print("[   {} {} {}   ]".format(mac, mac_ip[mac], time.time() - time_starts[mac]))



if __name__ == '__main__':
    dhcp_server = DHCP_server()
    dhcp_server.server()
    print("for show enter 1")
    while input() != "1":
        pass
    dhcp_server.show_clients()