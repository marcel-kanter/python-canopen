from canopen.node.service import Service


class PDOConsumer(Service):
	def __init__(self):
		Service.__init__(self)
	
	def attach(self, node):
		""" Attaches the service to a node. It does NOT append or assign this service to the node. """
		Service.attach(self, node)
		self._identifier_sync = 0x80
		self._identifier_rx = 0x200 + self._node.id
		self._node.network.subscribe(self.on_sync, self._identifier_sync)
		self._node.network.subscribe(self.on_pdo, self._identifier_rx)
		
	def detach(self):
		""" Detaches the service from the node. It does NOT remove or delete the service from the node. """
		if self._node == None:
			raise RuntimeError()
		self._node.network.unsubscribe(self.on_sync, self._identifier_sync)
		self._node.network.unsubscribe(self.on_pdo, self._identifier_rx)
		Service.detach(self)
	
	def on_pdo(self, message):
		pass
	
	def on_sync(self, message):
		pass
