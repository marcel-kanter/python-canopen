from canopen.node.service import Service


class PDOProducer(Service):
	def __init__(self):
		Service.__init__(self)
		self._callbacks = {"sync": [], "pdo": []}
	
	def attach(self, node):
		""" Attaches the ``PDOProducer`` to a ``Node``. It does NOT append or assign this ``PDOProducer`` to the ``Node``. """
		Service.attach(self, node)
		self._identifier_sync = 0x80
		self._identifier_tx = 0x180 + self._node.id
		self._node.network.subscribe(self.on_sync, self._identifier_sync)
		self._node.network.subscribe(self.on_pdo, self._identifier_tx)
		
	def detach(self):
		""" Detaches the ``PDOProducer`` from the ``Node``. It does NOT remove or delete the ``PDOProducer`` from the ``Node``. """
		if self._node == None:
			raise RuntimeError()
		self._node.network.unsubscribe(self.on_sync, self._identifier_sync)
		self._node.network.unsubscribe(self.on_pdo, self._identifier_tx)
		Service.detach(self)
	
	def on_pdo(self, message):
		if not message.is_remote_frame:
			return
		self.notify("pdo")
	
	def on_sync(self, message):
		self.notify("sync")
