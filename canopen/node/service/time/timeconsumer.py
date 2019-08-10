import canopen.objectdictionary
from canopen.node.service import Service
from canopen.objectdictionary import Variable


class TIMEConsumer(Service):
	
	_helper_variable = Variable("helper", 0, 0, canopen.objectdictionary.TIME_OF_DAY)
	
	def __init__(self):
		Service.__init__(self)
		self._identifier = 0x100
		self._callbacks = {"time": []}
	
	def attach(self, node):
		""" Attaches the ``TIMEConsumer`` to a ``Node``. It does NOT append or assign this ``TIMEConsumer`` to the ``Node``. """
		Service.attach(self, node)
		self._node.network.subscribe(self.on_time, self._identifier)
	
	def detach(self):
		""" Detaches the ``TIMEConsumer`` from the ``Node``. It does NOT remove or delete the ``TIMEConsumer`` from the ``Node``. """
		if self._node == None:
			raise RuntimeError()
		self._node.network.unsubscribe(self.on_time, self._identifier)
		Service.detach(self)
	
	def on_time(self, message):
		""" Message handler for incoming SYNC messages. """
		if message.is_remote_frame:
			return
		if message.dlc < 6:
			return
		
		t = self._helper_variable.decode(message.data)
		self.notify("time", self._node, t)
