from queue import Queue
from threading import Thread

class Router:
    def __init__(self, name, interfaces):
        self.name = name
        
        self.interfaces = interfaces
        self.interfaces_queues = [Queue(maxsize=100) for _ in range(len(interfaces))]

        self.routing_table = {}
        self.arp_table = {}
        
    # def add_route(self, destination, interface):
    #     self.routing_table[destination] = interface
    
    # def add_arp_entry(self, ip, mac):
    #     self.arp_table[ip] = mac
    
    def start():
        for i, interface in enumerate(self.interfaces):
            t = Thread(target=interface.start, args=(self.interfaces_queues[i],))
            t.start()
        
        t = Thread(target=self.mainloop)
        t.start()

    def mainloop(self):
        while True:
            for i, q in enumerate(self.interfaces_queues):
                if not q.empty():
                    packet = q.get()
                    self.handle_packet(i, packet)
    
    def handle_packet(self, interface, packet):
        next_hop = self.routing_table[packet.destination]
        # send packet to the next hop

