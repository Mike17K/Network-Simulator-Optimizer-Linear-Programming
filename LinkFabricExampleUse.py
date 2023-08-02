from MainPackage.LinkFabric.LinkFabric import LinkFabric
from MainPackage.Interface.Interface import Interface
from MainPackage.Packet.Packet import Packet


i1 = Interface("192.168.0.0") # mac: atribute for custom mac andress
i2 = Interface("192.168.0.1") # mac: atribute for custom mac andress

l1 = LinkFabric(i1, i2)

i1.start()
i2.start()

# the interface 1 wants to send a packet to the interface 2

pakcet1 = Packet(i1.ipv4, i2.ipv4, "Hello World from 1")
pakcet2 = Packet(i2.ipv4, i1.ipv4, "Hello World from 2")


i1.sendPacket(pakcet1)
i1.sendPacket(pakcet1)
i1.sendPacket(pakcet1)
i1.sendPacket(pakcet1)
i2.sendPacket(pakcet2)
i2.sendPacket(pakcet2)
i2.sendPacket(pakcet2)
i2.sendPacket(pakcet2)


# end the program
input("Press Enter to end...")
i1.stop()
i2.stop()
    