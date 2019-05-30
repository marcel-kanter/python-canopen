import struct
import can
from .service import Service


class NMTSlave(Service):
	def __init__(self):
		Service.__init__(self)
		self._state = 0
		self._toggle_bit = 0
	
	def attach(self, node):
		Service.attach(self, node)
		self._state = 0
		self._toggle_bit = 0
		self._node.network.subscribe(self.on_node_control, 0x000)
		self._node.network.subscribe(self.on_error_control, 0x700 + self._node.id)
	
	def detach(self):
		if self._node == None:
			raise RuntimeError()
		
		self._node.network.unsubscribe(self.on_error_control, 0x700 + self._node.id)
		self._node.network.unsubscribe(self.on_node_control, 0x000)
		Service.detach(self)
	
	def on_error_control(self, message):
		if not message.is_remote_frame:
			return
		if message.dlc != 1:
			return
		
		response = can.Message(arbitration_id = 0x700 + self._node.id, is_extended_id = False, data = [self._toggle_bit | self._state])
		self._node.network.send(response)
		
		self._toggle_bit ^= 0x80
	
	def on_node_control(self, message):
		if message.dlc != 2:
			return
		
		command, address = struct.unpack("<BB", message.data)
		
		if address == self._node.id or address == 0:
			if command == 0x01: # Start (enter NMT operational)
				self._state = 0x05
			if command == 0x02: # Stop (enter to NMT stopped)
				self._state = 0x04
			if command == 0x80: # Enter NMT pre-operational
				self._state = 0x7F
			if command == 0x81: # Enter NMT reset application
				self._state = 0x00
				self._toggle_bit = 0x00
				self._state = 0x7F
			if command == 0x82: # Enter NMT reset communication
				self._state = 0x00
				self._toggle_bit = 0x00
				self._state = 0x7F
	
	@property
	def state(self):
		return self._state
