import struct
import can
from canopen.node.service import Service
from canopen.nmt.states import *


class NMTSlave(Service):
	""" NMTSlave service.
	
	This class is an implementation of the NMT slave. The nmt state of the node can be accessed by the state property.
	"""
	def __init__(self):
		Service.__init__(self)
		self._state = 0
		self._toggle_bit = 0
		self._callbacks = {"start": [], "stop": [], "pause": [], "reset": []}
	
	def attach(self, node):
		""" Attaches the service to a node. It does NOT append or assign this service to the node. """
		Service.attach(self, node)
		self._state = 0
		self._toggle_bit = 0
		self._identifier_ec = 0x700 + self._node.id
		self._node.network.subscribe(self.on_node_control, 0x000)
		self._node.network.subscribe(self.on_error_control, self._identifier_ec)
	
	def detach(self):
		""" Detaches the service from the node. It does NOT remove or delete the service from the node. """
		if self._node == None:
			raise RuntimeError()
		self._node.network.unsubscribe(self.on_error_control, self._identifier_ec)
		self._node.network.unsubscribe(self.on_node_control, 0x000)
		Service.detach(self)
	
	def on_error_control(self, message):
		""" Handler for received error control requests. """
		if not message.is_remote_frame:
			return
		if message.dlc != 1:
			return
		
		# Do not respond to error control request in initialization state
		if self._state == INITIALIZATION:
			return
		
		response = can.Message(arbitration_id = self._identifier_ec, is_extended_id = False, data = [self._toggle_bit | (self._state & 0x7F)])
		self._node.network.send(response)
		
		self._toggle_bit ^= 0x80
	
	def on_node_control(self, message):
		""" Handler for received node control requests. """
		if message.dlc != 2:
			return
		
		command, address = struct.unpack("<BB", message.data)
		
		if address == self._node.id or address == 0:
			if command == 0x01: # Start (enter NMT operational)
				self.notify("start", self._node)
			if command == 0x02: # Stop (enter to NMT stopped)
				self.notify("stop", self._node)
			if command == 0x80: # Enter NMT pre-operational
				self.notify("pause", self._node)
			if command == 0x81: # Enter NMT reset application
				self.state = INITIALIZATION
				self.notify("reset", self._node)
			if command == 0x82: # Enter NMT reset communication
				self.state = INITIALIZATION
				self.state = PRE_OPERATIONAL
	
	@property
	def state(self):
		return self._state
	
	@state.setter
	def state(self, value):
		if value not in [INITIALIZATION, STOPPED, OPERATIONAL, PRE_OPERATIONAL]:
			raise ValueError()
		
		if self._state == INITIALIZATION:
			# In initialization state, only the transition to pre-operational state is allowed.
			if value != PRE_OPERATIONAL: 
				raise ValueError()
			self._toggle_bit = 0x00
		
		self._state = value 
