import struct
from canopen.node.service import Service


class SYNCConsumer(Service):
	def __init__(self):
		Service.__init__(self)
		self._identifier = 0x80
		self._callbacks = {"sync": []}
	
	def attach(self, node):
		""" Attaches the service to a node. It does NOT append or assign this service to the node. """
		Service.attach(self, node)
		self._node.network.subscribe(self.on_sync, self._identifier)
	
	def detach(self):
		""" Detaches the service from the node. It does NOT remove or delete the service from the node. """
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
