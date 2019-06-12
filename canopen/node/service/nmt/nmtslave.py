import struct
import can
from canopen.node.service import Service


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
		self._node.network.subscribe(self.on_node_control, 0x000)
		self._node.network.subscribe(self.on_error_control, 0x700 + self._node.id)
	
	def detach(self):
		""" Detaches the service from the node. It does NOT remove or delete the service from the node. """
		if self._node == None:
			raise RuntimeError()
		
		self._node.network.unsubscribe(self.on_error_control, 0x700 + self._node.id)
		self._node.network.unsubscribe(self.on_node_control, 0x000)
		Service.detach(self)
	
	def add_callback(self, callback, event):
		""" Adds the given callback to the event. """
		if not callable(callback):
			raise TypeError()
		if not event in self._callbacks:
			raise ValueError()
		
		self._callbacks[event].append(callback)
	
	def remove_callback(self, callback, event):
		""" Removes the callback from the event. """
		if not callable(callback):
			raise TypeError()
		if not event in self._callbacks:
			raise ValueError()
		
		self._callbacks[event].remove(callback)
	
	def notify(self, event, *args):
		""" Call the callbacks for the given event. """
		if not event in self._callbacks:
			raise ValueError()
		
		for callback in self._callbacks[event]:
			try:
				callback(event, self._node, *args)
			except:
				pass
	
	def on_error_control(self, message):
		""" Handler for received error control requests. """
		if not message.is_remote_frame:
			return
		if message.dlc != 1:
			return
		
		# Do not respond to error control request in initialization state
		if self._state == 0x00:
			return
		
		response = can.Message(arbitration_id = 0x700 + self._node.id, is_extended_id = False, data = [self._toggle_bit | self._state])
		self._node.network.send(response)
		
		self._toggle_bit ^= 0x80
	
	def on_node_control(self, message):
		""" Handler for received node control requests. """
		if message.dlc != 2:
			return
		
		command, address = struct.unpack("<BB", message.data)
		
		if address == self._node.id or address == 0:
			if command == 0x01: # Start (enter NMT operational)
				self.notify("start")
			if command == 0x02: # Stop (enter to NMT stopped)
				self.notify("stop")
			if command == 0x80: # Enter NMT pre-operational
				self.notify("pause")
			if command == 0x81: # Enter NMT reset application
				self.state = 0x00
				self.notify("reset")
			if command == 0x82: # Enter NMT reset communication
				self.state = 0x00
				self.state = 0x7F
	
	@property
	def state(self):
		return self._state
	
	@state.setter
	def state(self, value):
		if value not in [0x00, 0x04, 0x05, 0x7F]:
			raise ValueError()
		
		if self._state == 0x00:
			# In initialization state, only the transition to pre-operational state is allowed.
			if value != 0x7F: 
				raise ValueError()
			self._toggle_bit = 0x00
		
		self._state = value 
