import sys
import os

if __name__ == "__main__":
	# Let import look in the CWD too
	sys.path.append(os.getcwd())

import time
import can
import canopen
import canopen.nmt


if __name__ == "__main__":
	bus = can.Bus(interface = "ixxat", channel = 0, bitrate = 10000)
	network = canopen.Network()
	dictionary = canopen.ObjectDictionary()
	node = canopen.LocalNode("node", 1, dictionary)
	
	network.attach(bus)
	network.add(node)
	
	print("press CTRL-C to quit")
	
	try:
		network["node"].nmt.send_heartbeat()
		node.nmt.state = canopen.nmt.PRE_OPERATIONAL
		network["node"].nmt.start_heartbeat(0.2)
	
		time.sleep(1)
	
		network[1].nmt.state = canopen.nmt.OPERATIONAL
		
	
		while True:
			time.sleep(1)
	except:
		pass
	
	del network["node"]
	network.detach()
	bus.shutdown()
