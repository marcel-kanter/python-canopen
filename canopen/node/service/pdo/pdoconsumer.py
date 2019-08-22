import canopen.node
from canopen.node.service import Service


class PDOConsumer(Service):
	def __init__(self):
		Service.__init__(self)
		self._callbacks = {"sync": [], "pdo": []}
		self._data = None
	
	def attach(self, node, cob_id_rx = None, cob_id_sync = None):
		""" Attaches the ``PDOConsumer`` to a ``Node``. It does NOT append or assign this ``PDOConsumer`` to the ``Node``. """
		if not isinstance(node, canopen.node.Node):
			raise TypeError()
		if cob_id_rx == None:
			cob_id_rx = 0x200 + node.id
		if cob_id_rx < 0 or cob_id_rx > 0xFFFFFFFF:
			raise ValueError()
		if cob_id_sync == None:
			cob_id_sync = 0x80
		if cob_id_sync < 0 or cob_id_sync > 0xFFFFFFFF:
			raise ValueError()
		
		Service.attach(self, node)
		self._cob_id_rx = cob_id_rx
		self._cob_id_sync = cob_id_sync
		
		if self._cob_id_sync & (1 << 29):
			self._node.network.subscribe(self.on_sync, self._cob_id_sync & 0x1FFFFFFF)
		else:
			self._node.network.subscribe(self.on_sync, self._cob_id_sync & 0x7FF)
		if self._cob_id_rx & (1 << 29):
			self._node.network.subscribe(self.on_pdo, self._cob_id_rx & 0x1FFFFFFF)
		else:
			self._node.network.subscribe(self.on_pdo, self._cob_id_rx & 0x7FF)
	
	def detach(self):
		""" Detaches the ``PDOConsumer`` from the ``Node``. It does NOT remove or delete the ``PDOConsumer`` from the ``Node``. """
		if self._node == None:
			raise RuntimeError()
		
		if self._cob_id_sync & (1 << 29):
			self._node.network.unsubscribe(self.on_sync, self._cob_id_sync & 0x1FFFFFFF)
		else:
			self._node.network.unsubscribe(self.on_sync, self._cob_id_sync & 0x7FF)
		if self._cob_id_rx & (1 << 29):
			self._node.network.unsubscribe(self.on_pdo, self._cob_id_rx & 0x1FFFFFFF)
		else:
			self._node.network.unsubscribe(self.on_pdo, self._cob_id_rx & 0x7FF)
		
		Service.detach(self)
	
	def on_pdo(self, message):
		if message.is_remote_frame:
			return
		if message.is_extended_id != bool(self._cob_id_rx & (1 << 29)):
			return
		self._data = message.data
		self.notify("pdo", self)
	
	def on_sync(self, message):
		if message.is_remote_frame:
			return
		if message.is_extended_id != bool(self._cob_id_sync & (1 << 29)):
			return
		self.notify("sync", self)
	
	@property
	def data(self):
		return self._data
	
	@data.setter
	def data(self, data):
		self._data = data
