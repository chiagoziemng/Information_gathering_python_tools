from scapy.all import ARP, Ether, srp
import socket

# This script checks and lists all IP addresses in the private network

def get_local_ip():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    return local_ip

def get_network_prefix(local_ip):
    parts = local_ip.split('.')
    return '.'.join(parts[:3]) + '.0/24'

def scan_network(ip_range):
    arp = ARP(pdst=ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp

    result = srp(packet, timeout=2, verbose=0)[0]

    devices = []
    for sent, received in result:
        devices.append({'ip': received.psrc, 'mac': received.hwsrc})
    
    return devices

local_ip = get_local_ip()
ip_range = get_network_prefix(local_ip)

print(f"Scanning network: {ip_range}")

devices = scan_network(ip_range)

output = "Available devices in the network:\n"
output += "IP Address\t\tMAC Address\n"
output += "-"*40 + "\n"

for device in devices:
    output += f"{device['ip']}\t\t{device['mac']}\n"

print(output)

# Save to file
with open("networkinfo.txt", "w") as file:
    file.write(output)
