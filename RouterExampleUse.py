from MainPackage.Router.Router import Router
from MainPackage.Interface.Interface import Interface
from MainPackage.Packet.Packet import Packet

router1 = Router("192.168.0.0", ["192.168.0.1","192.168.0.2"])
router2 = Router("192.168.1.0", ["192.168.1.1","192.168.1.2"])

Interface.link("192.168.0.1","192.168.1.2")

router1.start()
router2.start()

packet = Packet("192.168.0.1","192.168.1.2","Hello World from 1")
router1.interfaces[router1.arp_table["192.168.0.1"]].sendPacket(packet)
router1.interfaces[router1.arp_table["192.168.0.1"]].sendPacket(packet)
router1.interfaces[router1.arp_table["192.168.0.1"]].sendPacket(packet)

# end the program
input("Press Enter to end...")
router1.stop()
router2.stop()