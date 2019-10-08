import sys
import os

if __name__ == "__main__":
	# Let import look in the CWD too
	sys.path.append(os.getcwd())

import time
import can
import canopen
import canopen.nmt


def fkt(event, service):
	print("heartbeat event")


if __name__ == "__main__":
	if len(sys.argv) != 2:
		print("Usage: " + sys.argv[0] + " <heartbeat-time>")
		print("")
		print("heartbeat-time: The time between the heartbeat message in seconds.")
		exit()
	
	bus = can.Bus(interface = "ixxat", channel = 0, bitrate = 10000)
	network = canopen.Network()
	dictionary = canopen.ObjectDictionary()
	node = canopen.RemoteNode("node", 1, dictionary)
	
	node.nmt.add_callback("heartbeat", fkt)
	
	network.attach(bus)
	network.add(node)
	
	print("press CTRL-C to quit")
	
	try:
		node.nmt.state = canopen.nmt.PRE_OPERATIONAL
		
		node.nmt.start_heartbeat(float(sys.argv[1]))
		
		while True:
			time.sleep(0.1)
	except:
		pass
	
	del network["node"]
	network.detach()
	bus.shutdown()
