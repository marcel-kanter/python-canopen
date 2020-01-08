import threading
import canopen.objectdictionary

from canopen.node.service import Service
from canopen.objectdictionary import Variable


class TIMEConsumer(Service):
	""" TIMEConsumer
	
	This class is an implementation of a TIME consumer.
	
	Callbacks
	"time": ("time", service, timestamp)
	"""
	
	_helper_variable = Variable("helper", 0, 0, canopen.objectdictionary.TIME_OF_DAY)
	
	def __init__(self, node):
		Service.__init__(self, node)
		self.add_event("time")
		self._cob_id_time = None
		
		self._time_condition = threading.Condition()
	
	def attach(self, cob_id_time = None):
		""" Attach handler. Must be called when the node gets attached to the network.
		
		:param cob_id_time: The COB ID for the TIME service. Bit 29 selects whether an extended frame is used. The CAN ID is masked out of the lowest 11 or 29 bits.
			It defaults to 0x100 if it is omitted or None.
		
		:raises: ValueError
		"""
		if cob_id_time == None:
			cob_id_time = 0x100
		if cob_id_time < 0 or cob_id_time > 0xFFFFFFFF:
			raise ValueError()
		if self.is_attached():
			self.detach()
		
		if cob_id_time & (1 << 29):
			self._node.network.subscribe(self.on_time, cob_id_time & 0x1FFFFFFF)
		else:
			self._node.network.subscribe(self.on_time, cob_id_time & 0x7FF)
		
		self._cob_id_time = cob_id_time
	
	def detach(self):
		""" Detach handler. Must be called when the node gets detached from the network.
		Raises RuntimeError if not attached.
		
		:raises: RuntimeError
		"""
		if not self.is_attached():
			raise RuntimeError()
		
		if self._cob_id_time & (1 << 29):
			self._node.network.unsubscribe(self.on_time, self._cob_id_time & 0x1FFFFFFF)
		else:
			self._node.network.unsubscribe(self.on_time, self._cob_id_time & 0x7FF)
		
		self._cob_id_time = None
	
	def is_attached(self):
		""" Returns True if the service is attached.
		"""
		return self._cob_id_time != None
	
	def on_time(self, message):
		""" Message handler for incoming SYNC messages. """
		if message.is_remote_frame:
			return
		if message.is_extended_id != bool(self._cob_id_time & (1 << 29)):
			return
		if message.dlc < 6:
			return
		
		timestamp = self._helper_variable.decode(message.data)
		self.notify("time", self, timestamp)
		with self._time_condition:
			self._time_condition.notify_all()
	
	def wait_for_time(self, timeout = None):
		""" Wait until the reception of TIME message or until a timeout occurs.
		
		When the timeout argument is present and not None, it should be a floating point number specifying a timeout for the operation in seconds (or fractions thereof).
		
		:param timeout: The time to wait in seconds, or ``None``
		
		:returns: True if the sync message was received, False if the timeout occured
		"""
		with self._time_condition:
			gotit = self._time_condition.wait(timeout)
		return gotit
