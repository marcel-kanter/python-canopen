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
	if len(sys.argv) != 2:
		print("Usage: " + sys.argv[0] + " <heartbeat-time>")
		print("")
		print("heartbeat-time: The time between the heartbeat message in seconds.")
		exit()
	
	bus = can.Bus(interface = "ixxat", channel = 0, bitrate = 10000)
	network = canopen.Network()
	dictionary = canopen.ObjectDictionary()
	node = canopen.LocalNode("node", 1, dictionary)
	
	network.attach(bus)
	network.add(node)
	
	print("press CTRL-C to quit")
	
	try:
		node.nmt.send_heartbeat()
		node.nmt.state = canopen.nmt.PRE_OPERATIONAL
		
		node.nmt.start_heartbeat(0.2)
	
		time.sleep(1)
	
		node.nmt.state = canopen.nmt.OPERATIONAL
		
		while True:
			time.sleep(0.1)
	except:
		pass
	
	del network["node"]
	network.detach()
	bus.shutdown()
