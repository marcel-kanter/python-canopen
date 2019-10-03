import struct
import can
import canopen.util
from canopen.node.service import Service
from canopen.nmt.states import *


class NMTSlave(Service):
	""" NMTSlave service.
	
	This class is an implementation of the NMT slave. The nmt state of the node can be accessed by the state property.
	
	Callbacks
	start, stop, pre-operational, reset-application, reset-communication, guarding
	"""
	def __init__(self):
		Service.__init__(self)
		self._state = 0
		self._toggle_bit = 0
		self._callbacks = {"start": [], "stop": [], "pre-operational": [], "reset-application": [], "reset-communication": [], "guarding" : []}
		
		self._counter = 0
		self._heartbeat_time = 0
		self._guard_time = 0
		self._life_time_factor = 0
		self._timer = canopen.util.Timer(self.timer_callback)
	
	def attach(self, node):
		""" Attaches the ``NMTSlave`` to a ``Node``. It does NOT add or assign this ``NMTSlave`` to the ``Node``.
		:param node: A canopen.Node, to which the service should be attached to. """
		Service.attach(self, node)
		self._state = 0
		self._toggle_bit = 0
		self._identifier_ec = 0x700 + self._node.id
		self._node.network.subscribe(self.on_node_control, 0x000)
		self._node.network.subscribe(self.on_error_control, self._identifier_ec)
	
	def detach(self):
		""" Detaches the ``NMTSlave`` from the ``Node``. It does NOT remove or delete the ``NMTSlave`` from the ``Node``. """
		if self._node == None:
			raise RuntimeError()
		self._node.network.unsubscribe(self.on_error_control, self._identifier_ec)
		self._node.network.unsubscribe(self.on_node_control, 0x000)
		self.stop()
		Service.detach(self)
	
	def start_heartbeat(self, heartbeat_time):
		""" Sends a heartbeat message and then every heartbeat_time seconds.
		:param heartbeat_time: The time between the heartbeat messages. """
		if heartbeat_time <= 0:
			raise ValueError()
		
		self._timer.cancel()
		
		self._heartbeat_time = heartbeat_time
		
		if self._state != INITIALIZATION:
			self.send_heartbeat()
			self._timer.start(self._heartbeat_time, True)
		
	def start_guarding(self, guard_time, life_time_factor):
		""" Starts monitoring the node guarding requests on reception of the next request. 
		:param guard_time: The time between the node guarding requests.
		:param life_time_factor: The life time factor as defined in DS301."""
		if guard_time <= 0:
			raise ValueError()
		if life_time_factor <= 0:
			raise ValueError()
		
		self._timer.cancel()
		
		self._guard_time = guard_time
		self._life_time_factor = life_time_factor
	
	def stop(self):
		""" Stops the error control methods. """
		self._timer.cancel()
		self._guard_time = 0
		self._life_time_factor = 0
		self._heartbeat_time = 0
	
	def send_heartbeat(self):
		""" Sends a heartbeat message. """
		message = can.Message(arbitration_id = self._identifier_ec, is_extended_id = False, data = [self._state & 0x7F])
		self._node.network.send(message)
	
	def send_guard_response(self):
		""" Sends a guard response. Basically a heartbeat message with the toggle bit. After sending the message, the toggle bit is inverted. """
		response = can.Message(arbitration_id = self._identifier_ec, is_extended_id = False, data = [self._toggle_bit | (self._state & 0x7F)])
		self._node.network.send(response)
		self._toggle_bit ^= 0x80
	
	def timer_callback(self):
		""" Handler for timer events. """
		self.send_heartbeat()
	
	def on_error_control(self, message):
		""" Handler for received error control requests. """
		if not message.is_remote_frame:
			return
		if message.dlc != 1:
			return
		
		# Do not respond to error control request in initialization state
		if self._state == INITIALIZATION:
			return
		
		self._counter = 0
		self.send_guard_response()
	
	def on_node_control(self, message):
		""" Handler for received node control requests. """
		if message.dlc != 2:
			return
		
		command, address = struct.unpack("<BB", message.data)
		
		if address == self._node.id or address == 0:
			if command == 0x01: # Start (enter NMT operational)
				self.notify("start", self)
			if command == 0x02: # Stop (enter to NMT stopped)
				self.notify("stop", self)
			if command == 0x80: # Enter NMT pre-operational
				self.notify("pre-operational", self)
			if command == 0x81: # Enter NMT reset application
				self.notify("reset-application", self)
			if command == 0x82: # Enter NMT reset communication
				self.notify("reset-communication", self)
	
	@property
	def state(self):
		return self._state
	
	@state.setter
	def state(self, value):
		if value not in [INITIALIZATION, STOPPED, OPERATIONAL, PRE_OPERATIONAL]:
			raise ValueError()
		
		if self._state == INITIALIZATION:
			# In initialization state, only the transition to pre-operational state is allowed.
			if value != PRE_OPERATIONAL and value != INITIALIZATION: 
				raise ValueError()
			
			self._toggle_bit = 0x00
			
			if self._heartbeat_time > 0:
				self.send_heartbeat()
				self._timer.start(self._heartbeat_time, True)
		else:
			if value == INITIALIZATION:
				self._timer.cancel()
		
		self._state = value 
