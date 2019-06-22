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
		""" Attaches the service to a node. It does NOT append or assign this service to the node. """
		Service.attach(self, node)
		self._node.network.subscribe(self.on_emcy, 0x80 + self._node.id)
	
	def detach(self):
		""" Detaches the service from the node. It does NOT remove or delete the service from the node. """
		if self._node == None:
			raise RuntimeError()
		
		self._node.network.unsubscribe(self.on_emcy, 0x80 + self._node.id)
		Service.detach(self)
		
	def on_emcy(self, message):
		error_code, error_register, data = struct.unpack("<HB5s", message.data)
		
		self.notify("emcy", self._node, error_code, error_register, data)
