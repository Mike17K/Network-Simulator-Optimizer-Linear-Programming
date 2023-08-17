from queue import Queue
from threading import Thread
from MainPackage.Interface.Interface import Interface
from MainPackage.Packet.Packet import Packet

import random

def generate_random_mac_address():
    mac_digits = [random.choice('0123456789ABCDEF') for _ in range(12)]
    mac_address = ':'.join(''.join(mac_digits[i:i+2]) for i in range(0, 12, 2))
    return mac_address


class Router:
    def __init__(self, ipv4, interfaces = [], mac = generate_random_mac_address()):
        '''
        ipv4: ipv4 address of the router
        interfaces: list of ipv4 of the interfaces
        mac: mac address of the router
        '''
        self.ipv4 = ipv4
        self.running = True

        self.mac = mac
        self.routing_table = {} # corilates ipv4 with interface
        self.arp_table = {} # corilates ipv4 with mac
        
        self.interfaces = {}
        for ip in interfaces:
            self.arp_table[ip] = generate_random_mac_address()
            interface = Interface(ip, mac = self.arp_table[ip])
            self.interfaces[self.arp_table[ip]] = interface

    def link(self, device,propagation_speed = 200000000):
        '''
        interface: interface object
        '''
        for interface in self.interfaces.values():
            for device_interface in device.interfaces.values():
                if interface.link is None and device_interface.link is None:
                    link = Interface.link(interface.ipv4, device_interface.ipv4,propagation_speed)
                    return link
        return None
    
    def start(self):
        for interface in self.interfaces.values():
            interface.start()
        th = Thread(target=self.handle_packets)
        th.start()
        
    def stop(self):
        for interface in self.interfaces.values():
            interface.stop()
        self.running = False
    
    def handle_packets(self):
        while self.running:
            for interface in self.interfaces.values():
                if not interface.receive_queue.empty():
                    packet = interface.receive_queue.get()
                    self.handle_packet(packet)

    def handle_packet(self, packet):

        '''
        Destination IP Address Lookup: The router performs a lookup in its routing table to find the best path for the packet to reach its destination. It compares the destination IP address in the packet with the entries in the routing table to determine the appropriate next hop or egress interface.
        '''

        interface_ip = packet.destination # this comes from the routing table
        if interface_ip not in self.arp_table.keys():
            print("Not found in arp table")
            return

        interface = self.interfaces[self.arp_table[interface_ip]]
        interface.sendPacket(packet)

        endpoint = interface.link.endpoint2 if interface.link.endpoint1.ipv4 == interface_ip else interface.link.endpoint1

        print("Packet sent thrue: ",interface_ip," to ",endpoint.ipv4," message: ",packet.payload)








'''
routing table for each entry:
    destination network: ipv4 address of the destination network
    interface: interface object
    mask: mask of the ipv4 address
    next_hop: ipv4 address of the next hop
    metric: metric of the route
    gateway: ipv4 address of the gateway
'''