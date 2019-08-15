from canopen.node.service import Service


class PDOConsumer(Service):
	def __init__(self):
		Service.__init__(self)
		self._callbacks = {"sync": [], "pdo": []}
		self._data = None
	
	def attach(self, node):
		""" Attaches the ``PDOConsumer`` to a ``Node``. It does NOT append or assign this ``PDOConsumer`` to the ``Node``. """
		Service.attach(self, node)
		self._identifier_sync = 0x80
		self._identifier_rx = 0x200 + self._node.id
		self._node.network.subscribe(self.on_sync, self._identifier_sync)
		self._node.network.subscribe(self.on_pdo, self._identifier_rx)
		
	def detach(self):
		""" Detaches the ``PDOConsumer`` from the ``Node``. It does NOT remove or delete the ``PDOConsumer`` from the ``Node``. """
		if self._node == None:
			raise RuntimeError()
		self._node.network.unsubscribe(self.on_sync, self._identifier_sync)
		self._node.network.unsubscribe(self.on_pdo, self._identifier_rx)
		Service.detach(self)
	
	def on_pdo(self, message):
		self._data = message.data
		self.notify("pdo", self)
	
	def on_sync(self, message):
		self.notify("sync", self)
	
	@property
	def data(self):
		return self._data
	
	@data.setter
	def data(self, data):
		self._data = data
