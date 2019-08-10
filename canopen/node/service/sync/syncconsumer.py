import struct
from canopen.node.service import Service


class SYNCConsumer(Service):
	def __init__(self):
		Service.__init__(self)
		self._callbacks = {"sync": []}
	
	def attach(self, node):
		""" Attaches the ``SYNCConsumer`` to a ``Node``. It does NOT append or assign this ``SYNCConsumer`` to the ``Node``. """
		Service.attach(self, node)
		self._identifier = 0x80
		self._node.network.subscribe(self.on_sync, self._identifier)
	
	def detach(self):
		""" Detaches the ``SYNCConsumer`` from the ``Node``. It does NOT remove or delete the ``SYNCConsumer`` from the ``Node``. """
		if self._node == None:
			raise RuntimeError()
		self._node.network.unsubscribe(self.on_sync, self._identifier)
		Service.detach(self)
	
	def on_sync(self, message):
		""" Message handler for incoming SYNC messages. """
		if message.is_remote_frame:
			return
		if message.dlc == 1:
			counter, = struct.unpack_from("<B", message.data)
		else:
			counter = None
		self.notify("sync", self._node, counter)
