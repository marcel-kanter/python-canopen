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
	
	def __init__(self):
		Service.__init__(self)
		self._callbacks = {"time": []}
	
	def attach(self, node, cob_id_time = None):
		""" Attaches the ``TIMEConsumer`` to a ``Node``. It does NOT add or assign this ``TIMEConsumer`` to the ``Node``.
		:param node: A canopen.Node, to which the service should be attached to.
		:param cob_id_time: The COB ID for the TIME service. Bit 29 selects whether an extended frame is used. The CAN ID is masked out of the lowest 11 or 29 bits.
			If it is omitted or None is passed, the value defaults to 0x100. """
		if cob_id_time == None:
			cob_id_time = 0x100
		if cob_id_time < 0 or cob_id_time > 0xFFFFFFFF:
			raise ValueError()
		
		Service.attach(self, node)
		self._cob_id_time = cob_id_time
		
		if self._cob_id_time & (1 << 29):
			self._node.network.subscribe(self.on_time, self._cob_id_time & 0x1FFFFFFF)
		else:
			self._node.network.subscribe(self.on_time, self._cob_id_time & 0x7FF)
	
	def detach(self):
		""" Detaches the ``TIMEConsumer`` from the ``Node``. It does NOT remove or delete the ``TIMEConsumer`` from the ``Node``. """
		if not self.is_attached():
			raise RuntimeError()
		if self._cob_id_time & (1 << 29):
			self._node.network.unsubscribe(self.on_time, self._cob_id_time & 0x1FFFFFFF)
		else:
			self._node.network.unsubscribe(self.on_time, self._cob_id_time & 0x7FF)
		Service.detach(self)
	
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
