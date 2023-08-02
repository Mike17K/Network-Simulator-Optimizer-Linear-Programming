from queue import Queue
from threading import Thread
import random
import time

class LinkFabric:
    def __init__(self, endpoint1 , endpoint2,propagation_speed = 200000000):
        '''
        endpoint1 , endpoint2: interface objects
            have queue: queue
            have ipv4: ipv4
        '''

        self.propagation_speed = propagation_speed

        self.endpoint1 = endpoint1
        self.endpoint2 = endpoint2

        self.endpoint1.connect(self)
        self.endpoint2.connect(self)

        self.isLocked = False
    
    def lock(self):
        self.isLocked = True
    
    def unlock(self):
        self.isLocked = False

    def sendPacket(self, packet):
        propagation_time = packet.size / self.propagation_speed
        time.sleep(propagation_time) # here instead of time we can use a variable to store time for more precise simulation

        if packet.source == self.endpoint1.ipv4:
            self.endpoint2.receive_queue.put(packet)
        elif packet.source == self.endpoint2.ipv4:
            self.endpoint1.receive_queue.put(packet)


