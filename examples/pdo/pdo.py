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
	bus = can.Bus(interface = "ixxat", channel = 0, bitrate = 500000)
	network = canopen.Network()
	dictionary = canopen.ObjectDictionary()
	local_node = canopen.LocalNode("local_node", 1, dictionary)
	remote_node = canopen.RemoteNode("remote_node", 20, dictionary)
	
	network.attach(bus)
	network.add(local_node)
	network.add(remote_node)
	
	print("press CTRL-C to quit")
	
	# transmit data from TPDO1 the local node
	local_node.tpdo[1].data = b"\x01\x02"
	local_node.tpdo[1].send()
	
	# transmit data to RPDO1 of the remote node
	remote_node.rpdo[1].data = b"\x20"
	remote_node.rpdo[1].send()
	
	try:		
		while True:
			time.sleep(0.1)
	except:
		pass
	
	del network["local_node"]
	del network["remote_node"]
	network.detach()
	bus.shutdown()
