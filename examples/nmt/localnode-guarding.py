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
	service.node.emcy.send(0x8130, 0x11, None)
	print("guarding event")


if __name__ == "__main__":
	if len(sys.argv) != 3:
		print("Usage: " + sys.argv[0] + " <guarding-time> <life-time-factor>")
		print("")
		print("gurading-time: The time between the guarding requests in seconds.")
		print("life-time-factor: The life time factor as defined in DS301.")
		exit()
	
	bus = can.Bus(interface = "ixxat", channel = 0, bitrate = 10000)
	network = canopen.Network()
	dictionary = canopen.ObjectDictionary()
	node = canopen.LocalNode("node", 1, dictionary)
	
	node.nmt.add_callback("guarding", fkt)
	
	network.attach(bus)
	network.add(node)
	
	print("press CTRL-C to quit")
	
	try:
		node.nmt.state = canopen.nmt.PRE_OPERATIONAL
		
		node.nmt.start_guarding(float(sys.argv[1]), int(sys.argv[2]))
	
		time.sleep(1)
	
		node.nmt.state = canopen.nmt.OPERATIONAL
		
		while True:
			time.sleep(0.1)
	except:
		pass
	
	del network["node"]
	network.detach()
	bus.shutdown()
