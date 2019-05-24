import struct
import canopen.node


class NMTSlave(object):
	def __init__(self):
		self._node = None
		self._state = 0
	
	def attach(self, node):
		if not isinstance(node, canopen.node.Node):
			raise TypeError()
		if self._node == node:
			raise ValueError()
		if self._node != None:
			self.detach()
		
		self._node = node
		self._node.network.subscribe(self.on_node_control, 0x000)
	
	def detach(self):
		self._node.network.unsubscribe(self.on_node_control, 0x000)
		self._node = None
	
	def on_node_control(self, message):
		if message.dlc != 2:
			return
		
		command, address = struct.unpack("<BB", message.data)
		
		if address == self._node.id or address == 0:
			if command == 0x01:
				self._state = 0x05 # Start (enter NMT operational)
			if command == 0x02:
				self._state = 0x04 # Stop (enter to NMT stopped)
			if command == 0x80:
				self._state = 0x7F # Enter NMT pre-operational
			if command == 0x81:
				self._state = 0x00 # Enter NMT reset application
			if command == 0x82:
				self._state = 0x00 # Enter NMT reset communication
	
	@property
	def state(self):
		return self._state
