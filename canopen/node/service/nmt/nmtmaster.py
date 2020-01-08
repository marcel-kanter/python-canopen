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
	def __init__(self, node):
		""" Initializes the service
		
		:param node: The node, to which this service belongs to.
			Must be of type canopen.node.Node
		
		:raises: TypeError
		"""
		Service.__init__(self, node)
		self.add_event("heartbeat")
		self.add_event("guarding")
		self._identifier_ec = None
		
		# The state and toggle bit of the next guarding response is unknown, but maybe the node is in initialization state. Pretend there was a previous guarding response with the inverted toggle bit.
		self._state = INITIALIZATION
		self._toggle_bit = 0x80
		self._counter = 0
		self._heartbeat_time = 0
		self._guard_time = 0
		self._life_time_factor = 0
		self._timer = canopen.util.Timer(self.timer_callback)
	
	def attach(self):
		""" Attach handler. Must be called when the node gets attached to the network.
		
		:raises: ValueError
		"""
		if self.is_attached():
			self.detach()
		
		identifier_ec = 0x700 + self._node.id
		
		self._node.network.subscribe(self.on_error_control, identifier_ec)
		
		self._identifier_ec = identifier_ec
	
	def detach(self):
		""" Detach handler. Must be called when the node gets detached from the network.
		Raises RuntimeError if not attached.
		
		:raises: RuntimeError
		"""
		if not self.is_attached():
			raise RuntimeError()
		
		self.stop()
		self._node.network.unsubscribe(self.on_error_control, self._identifier_ec)
		
		self._identifier_ec = None
	
	def is_attached(self):
		""" Returns True if the service is attached.
		"""
		return self._identifier_ec != None
	
	def send_command(self, command):
		""" Sends a NMT command.
		Raises ValueError if the command is out of range.
		
		:param command: The command to send.
			Must be an integer in the range 0x00 ... 0xFF
		
		:raises: ValueError
		"""
		if int(command) < 0x00 or int(command) > 0xFF:
			raise ValueError()
		
		d = struct.pack("<BB", command, self._node.id)
		request = can.Message(arbitration_id = 0x000, is_extended_id = False, data = d)
		self._node.network.send(request)
	
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
			self.send_command(0x81)
			# The toggle bit of the next guarding response should be 0. Pretend there was a previous guarding response with the inverted toggle bit.
			self._toggle_bit = 0x80
		if value == STOPPED:
			self.send_command(0x02)
		if value == OPERATIONAL:
			self.send_command(0x01)
		if value == PRE_OPERATIONAL:
			self.send_command(0x80)
