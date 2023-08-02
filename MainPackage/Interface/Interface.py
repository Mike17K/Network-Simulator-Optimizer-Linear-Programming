from queue import Queue
from threading import Thread
from MainPackage.LinkFabric.LinkFabric import LinkFabric as LinkFabric
import random

def generate_random_mac_address():
    mac_digits = [random.choice('0123456789ABCDEF') for _ in range(12)]
    mac_address = ':'.join(''.join(mac_digits[i:i+2]) for i in range(0, 12, 2))
    return mac_address


class Interface:
    INSTANCES = {}
    def __init__(self, ipv4, mac = generate_random_mac_address()):
        self.ipv4 = ipv4
        self.mac = mac
        self.transmit_queue = Queue(maxsize=100) # transmit queue
        self.receive_queue = Queue(maxsize=100) # receive queue

        self.link = None

        self.send_thread_running = True

        Interface.INSTANCES[ipv4] = self

    def start(self):
        self.send_thread = Thread(target=self.send)

        self.send_thread.start()

    def stop(self):
        self.listen_thread_running = False
        self.send_thread_running = False

    def sendPacket(self, packet):
        self.transmit_queue.put(packet)

    def send(self):
        if self.link is None: return # if the interface is not connected to a link
        while self.send_thread_running:
            if not self.transmit_queue.empty():
                if not self.link.isLocked:
                    self.link.lock()
                    packet = self.transmit_queue.get()
                    self.link.sendPacket(packet)
                    self.link.unlock()

    def connect(self, link):
        self.link = link
    
    @staticmethod
    def link(ipv4_1, ipv4_2):
        interface1 = Interface.INSTANCES[ipv4_1]
        interface2 = Interface.INSTANCES[ipv4_2]
        
        link = LinkFabric(interface1, interface2)
        interface1.connect(link)
        interface2.connect(link)
        return link