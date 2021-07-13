import random
import socket
import struct
import json

def ip2int(addr):
    return struct.unpack("!I", socket.inet_aton(addr))[0]


f = open('configs.json',)
data = json.load(f)
start = data['range']['from']
stop = data['range']['to']
f.close()
start_num = ip2int(start)
stop_num = ip2int(stop)
random_ip = socket.inet_ntoa(struct.pack('>I', random.randint(start_num, stop_num)))
parts = random_ip.split(".")
ip = ''
for part in parts:
    print(hex(int(part)))
    hex_part = hex(int(part))
    ip += '\\' + hex_part[1:]

print(ip)
next_server = ''
server = "127.0.0.1".split(".")
for part in server:
    hex_part = hex(int(part))
    next_server += '\\' + hex_part[1:]
print(next_server)