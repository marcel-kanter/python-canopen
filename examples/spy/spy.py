import sys
import os

if __name__ == "__main__":
	# Let import look in the CWD too
	sys.path.append(os.getcwd())


import can
import canopen
from canopenspy import SpyNode


if __name__ == "__main__":
	bus = can.Bus(interface = "ixxat", channel = 0, bitrate = 100000)
	network = canopen.Network()
	spy = SpyNode("1", 1)
	
	network.attach(bus)
	spy.attach(network)
	
	spy.detach()
	network.detach()
	bus.shutdown()
