import canopen.objectdictionary
from canopen.node.service import Service
from canopen.objectdictionary import Variable


class TIMEConsumer(Service):
	
	_helper_variable = Variable("helper", 0, 0, canopen.objectdictionary.TIME_OF_DAY)
	
	def __init__(self):
		Service.__init__(self)
		self._callbacks = {"time": []}
	
	def attach(self, node, cob_id_time = None):
		""" Attaches the ``TIMEConsumer`` to a ``Node``. It does NOT append or assign this ``TIMEConsumer`` to the ``Node``. """
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
		if self._node == None:
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
		
		t = self._helper_variable.decode(message.data)
		self.notify("time", self, t)
