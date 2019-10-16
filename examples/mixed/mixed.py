import sys
import os

if __name__ == "__main__":
	# Let import look in the CWD too
	sys.path.append(os.getcwd())

import can
import canopen
import canopen.nmt


def process_message(message, network):
	if message.is_extended_id:
		print(message)
	
		if message.arbitration_id == 0x2000:
			network["somenode"].nmt.state = canopen.nmt.PRE_OPERATIONAL
	

# First create a bus
bus = can.Bus(interface = "ixxat", channel = 0, bitrate = 10000)

# It's possible to use the can bus now, as described in the python-can documentation.
# You may send and receive messages, etc.
msg = can.Message(arbitration_id = 0x1000, is_extended_id = True, dlc = 0)
bus.send(msg)

# Create the canopen Network instance and attach it to the bus
dictionary = canopen.ObjectDictionary()
node = canopen.RemoteNode("somenode", 1, dictionary)

network = canopen.Network()
# A call with builtin_notifier = False is needed for proper operation.
network.attach(bus, builtin_notifier = False)

network.add(node)

# Simple endless-loop "notifier". This is a stripped version of the internal code of ``can.Notifier``
_finish = False
msg = None
while not _finish:
	if msg is not None:
		# check if msg is a CAN message and process it
		process_message(msg, network)
		
		# pass the msg to the message handler of network
		network.on_message(msg)
		
	# Receive new message, if any
	msg = bus.recv(1.0)
	
# Detach the canopen Network before shutdown of the can bus.
network.detach()

# The can bus is still open and usable at this point.
msg = can.Message(arbitration_id = 0x1001, is_extended_id = True, dlc = 0)
bus.send(msg)

# Clean up
bus.shutdown()