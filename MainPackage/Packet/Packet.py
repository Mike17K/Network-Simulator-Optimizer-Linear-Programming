

class Packet:
    def __init__(self, source, destination, payload):
        '''
        source: ipv4 address of the source
        destination: ipv4 address of the destination
        payload: the data to be sent
        '''
        self.source = source
        self.destination = destination
        self.payload = payload

        self.size = len(payload) * 8 # bits
    
    def __str__(self):
        return "Packet: " + self.payload