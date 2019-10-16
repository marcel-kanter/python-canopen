import struct
import can
import canopen.util
from canopen.node.service import Service
from canopen.nmt.states import *


class NMTMaster(Service):
	""" NMTMaster service.
	
	This class is an implementation of the NMT master. The nmt state of the node can be accessed by the state property.
	
	Callbacks
	"heartbeat": ("heartbeat", service)
	"guarding": ("guarding", service)
	"""
	def __init__(self):
		Service.__init__(self)
		self._state = 0
		self._toggle_bit = 0x00
		self._callbacks = {"heartbeat": [], "guarding": []}
		
		self._counter = 0
		self._heartbeat_time = 0
		self._guard_time = 0
		self._life_time_factor = 0
		self._timer = canopen.util.Timer(self.timer_callback)
	
	def attach(self, node):
		""" Attaches the ``NMTMaster`` to a ``Node``. It does NOT add or assign this ``NMTMaster`` to the ``Node``.
		:param node: A canopen.Node, to which the service should be attached to. """
		Service.attach(self, node)
		self._state = 0
		# The toggle bit of the next guarding response is unknown, but maybe the node is in initialization state. Pretend there was a previous guarding response with the inverted toggle bit.
		self._toggle_bit = 0x80
		self._identifier_ec = 0x700 + self._node.id
		self._node.network.subscribe(self.on_error_control, self._identifier_ec)
	
	def detach(self):
		""" Detaches the ``NMTMaster`` from the ``Node``. It does NOT remove or delete the ``NMTMaster`` from the ``Node``. """
		if not self.is_attached():
			raise RuntimeError()
		
		self._node.network.unsubscribe(self.on_error_control, self._identifier_ec)
		self.stop()
		
		Service.detach(self)
	
	def start_heartbeat(self, heartbeat_time):
		""" Starts montioring the heartbeat messages.
		:param heartbeat_time: The time between the heartbeat messages. """
		if heartbeat_time <= 0:
			raise ValueError()
		
		self._timer.cancel()
		
		self._heartbeat_time = heartbeat_time
		self._counter = 1
	
	def start_guarding(self, guard_time, life_time_factor):
		""" Sends a node guarding request and then every guard_time seconds.
		:param guard_time: The time between the node guarding requests.
		:param life_time_factor: The life time factor as defined in DS301."""
		if guard_time <= 0:
			raise ValueError()
		if life_time_factor <= 0:
			raise ValueError()
		
		self._timer.cancel()
		
		self._guard_time = guard_time
		self._life_time_factor = life_time_factor
		self._counter = 1
		self.send_guard_request()
		self._timer.start(self._guard_time, True)
	
	def stop(self):
		""" Stops the error control methods. """
		self._timer.cancel()
		self._guard_time = 0
		self._life_time_factor = 0
		self._heartbeat_time = 0
	
	def send_guard_request(self):
		""" Sends a guard request. """
		message = can.Message(arbitration_id = self._identifier_ec, is_extended_id = False, is_remote_frame = True, dlc = 1)
		self._node.network.send(message)
	
	def timer_callback(self):
		""" Handler for timer events. """
		if self._heartbeat_time > 0:
			self.notify("heartbeat", self)
		elif self._guard_time > 0 and self._life_time_factor > 0:
			if self._counter >= self._life_time_factor:
				self.notify("guarding", self)
			self._counter += 1
			self.send_guard_request()
		else:
			self._timer.cancel()
	
	def on_error_control(self, message):
		""" Handler for error control responses. It catches all status messages from the remote node and updates the state property. """
		if message.is_remote_frame:
			return
		if message.dlc != 1:
			return
		
		# Check toggle bit only when node guarding is active
		if self._guard_time <= 0 or self._life_time_factor <= 0 or message.data[0] & 0x80 == self._toggle_bit ^ 0x80:
			self._counter = 0
			self._state = message.data[0] & 0x7F
		self._toggle_bit = message.data[0] & 0x80
		if self._heartbeat_time > 0:
			self._timer.cancel()
			self._timer.start(self._heartbeat_time, False)
	
	@property
	def state(self):
		return self._state
	
	@state.setter
	def state(self, value):
		if value not in [INITIALIZATION, STOPPED, OPERATIONAL, PRE_OPERATIONAL]:
			raise ValueError()
		
		if value == INITIALIZATION:
			command = 0x81
			# The toggle bit of the next guarding response should be 0. Pretend there was a previous guarding response with the inverted toggle bit.
			self._toggle_bit = 0x80
		if value == STOPPED:
			command = 0x02
		if value == OPERATIONAL:
			command = 0x01
		if value == PRE_OPERATIONAL:
			command = 0x80
		
		d = struct.pack("<BB", command, self._node.id)
		request = can.Message(arbitration_id = 0x000, is_extended_id = False, data = d)
		self._node.network.send(request)
