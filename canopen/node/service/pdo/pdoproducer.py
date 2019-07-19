from canopen.node.service import Service


class PDOProducer(Service):
	def __init__(self):
		Service.__init__(self)
	
	def attach(self, node):
		""" Attaches the service to a node. It does NOT append or assign this service to the node. """
		Service.attach(self, node)
		self._identifier_sync = 0x80
		self._identifier_tx = 0x180 + self._node.id
		self._node.network.subscribe(self.on_sync, self._identifier_sync)
		self._node.network.subscribe(self.on_pdo, self._identifier_tx)
		
	def detach(self):
		""" Detaches the service from the node. It does NOT remove or delete the service from the node. """
		if self._node == None:
			raise RuntimeError()
		self._node.network.unsubscribe(self.on_sync, self._identifier_sync)
		self._node.network.unsubscribe(self.on_pdo, self._identifier_tx)
		Service.detach(self)
	
	def on_pdo(self, message):
		if not message.is_remote_frame:
			return
		pass
	
	def on_sync(self, message):
		pass
