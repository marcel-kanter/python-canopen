import struct
import can
from canopen.node.service import Service
from canopen.nmt.states import *


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
		self._identifier_ec = 0x700 + self._node.id
		self._node.network.subscribe(self.on_error_control, self._identifier_ec)
	
	def detach(self):
		""" Detaches the service from the node. It does NOT remove or delete the service from the node. """
		if self._node == None:
			raise RuntimeError()
		self._node.network.unsubscribe(self.on_error_control, self._identifier_ec)
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
		if value not in [INITIALIZATION, STOPPED, OPERATIONAL, PRE_OPERATIONAL]:
			raise ValueError()
		
		if value == INITIALIZATION:
			command = 0x81
		if value == STOPPED:
			command = 0x02
		if value == OPERATIONAL:
			command = 0x01
		if value == PRE_OPERATIONAL:
			command = 0x80
		
		d = struct.pack("<BB", command, self._node.id)
		request = can.Message(arbitration_id = 0x000, is_extended_id = False, data = d)
		self._node.network.send(request)
