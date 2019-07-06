import can
import struct
from canopen.node.service import Service


class SYNCProducer(Service):
	def __init__(self):
		Service.__init__(self)
	
	def attach(self, node):
		Service.attach(self, node)
		self._identifier = 0x80
	
	def send(self, counter = None):
		""" Sends a SYNC message on the bus. If counter is None, no data is used in the SYNC message."""
		if counter == None:
			message = can.Message(arbitration_id = self._identifier, is_extended_id = False, dlc = 0)
		else:
			d = struct.pack("<B", int(counter))
			message = can.Message(arbitration_id = self._identifier, is_extended_id = False, data = d)
		self._node.network.send(message)
