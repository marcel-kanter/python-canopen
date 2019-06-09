import struct
import can
from canopen.node.service import Service


class NMTMaster(Service):
	""" NMTMaster service.
	
	This class is an implementation of the NMT master. The nmt state of the node can be accessed by the state property.
	"""
	def __init__(self):
		Service.__init__(self)
		self._state = 0

	def attach(self, node):
		""" Attaches the service to a node. It does NOT append or assign this service to the node. """
		Service.attach(self, node)
		self._state = 0
		self._node.network.subscribe(self.on_error_control, 0x700 + self._node.id)
	
	def detach(self):
		""" Detaches the service from the node. It does NOT remove or delete the service from the node. """
		if self._node == None:
			raise RuntimeError()
		
		self._node.network.unsubscribe(self.on_error_control, 0x700 + self._node.id)
		Service.detach(self)
	
	def on_error_control(self, message):
		""" Handler for error control requests. It catches all status messages from the remote node and updates the state property. """
		if message.is_remote_frame:
			return
		if message.dlc != 1:
			return
		
		self._state = message.data[0] & 0x7F
	
	@property
	def state(self):
		return self._state
	
	@state.setter
	def state(self, value):
		if value not in [0x00, 0x04, 0x05, 0x7F]:
			raise ValueError()
		
		if value == 0x00: # NMT reset application
			command = 0x81
		if value == 0x04: # NMT stopped
			command = 0x02
		if value == 0x05: # NMT Operational
			command = 0x01
		if value == 0x7F: # NMT pre-operational
			command = 0x80
		
		d = struct.pack("<BB", command, self._node.id)
		request = can.Message(arbitration_id = 0x00, is_extended_id = False, data = d)
		self._node.network.send(request)
