import struct
from canopen.node.service import Service


class EMCYConsumer(Service):
	""" EMCY consumer
	
	This class is an implementation of a DS301 EMCY consumer. 
	"""
	def __init__(self):
		Service.__init__(self)
		self._callbacks = {"emcy": []}
	
	def attach(self, node):
		""" Attaches the ``EMCYConsumer`` to a ``Node``. It does NOT add or assign this ``EMCYConsumer`` to the ``Node``. """
		Service.attach(self, node)
		self._identifier_rx = 0x80 + self._node.id
		self._node.network.subscribe(self.on_emcy, self._identifier_rx)
	
	def detach(self):
		""" Detaches the ``EMCYConsumer`` from the ``Node``. It does NOT remove or delete the ``EMCYConsumer`` from the ``Node``. """
		if self._node == None:
			raise RuntimeError()
		self._node.network.unsubscribe(self.on_emcy, self._identifier_rx)
		Service.detach(self)
		
	def on_emcy(self, message):
		error_code, error_register, data = struct.unpack("<HB5s", message.data)
		
		self.notify("emcy", self, error_code, error_register, data)
