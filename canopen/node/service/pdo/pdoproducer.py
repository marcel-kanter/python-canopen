import canopen.node
from canopen.node.service import Service


class PDOProducer(Service):
	def __init__(self):
		Service.__init__(self)
		self._callbacks = {"sync": [], "pdo": []}
		self._data = None
	
	def attach(self, node, cob_id_tx = None, cob_id_sync = None):
		""" Attaches the ``PDOProducer`` to a ``Node``. It does NOT append or assign this ``PDOProducer`` to the ``Node``. """
		if not isinstance(node, canopen.node.Node):
			raise TypeError()
		if cob_id_tx == None:
			cob_id_tx = 0x180 + node.id
		if cob_id_tx < 0 or cob_id_tx > 0xFFFFFFFF:
			raise ValueError()
		if cob_id_sync == None:
			cob_id_sync = 0x80
		if cob_id_sync < 0 or cob_id_sync > 0xFFFFFFFF:
			raise ValueError()
		
		Service.attach(self, node)
		self._cob_id_tx = cob_id_tx
		self._cob_id_sync = cob_id_sync
		
		if self._cob_id_sync & (1 << 29):
			self._node.network.subscribe(self.on_sync, self._cob_id_sync & 0x1FFFFFFF)
		else:
			self._node.network.subscribe(self.on_sync, self._cob_id_sync & 0x7FF)
		if self._cob_id_tx & (1 << 29):
			self._node.network.subscribe(self.on_pdo, self._cob_id_tx & 0x1FFFFFFF)
		else:
			self._node.network.subscribe(self.on_pdo, self._cob_id_tx & 0x7FF)
		
	def detach(self):
		""" Detaches the ``PDOProducer`` from the ``Node``. It does NOT remove or delete the ``PDOProducer`` from the ``Node``. """
		if self._node == None:
			raise RuntimeError()
		
		if self._cob_id_sync & (1 << 29):
			self._node.network.unsubscribe(self.on_sync, self._cob_id_sync & 0x1FFFFFFF)
		else:
			self._node.network.unsubscribe(self.on_sync, self._cob_id_sync & 0x7FF)
		if self._cob_id_tx & (1 << 29):
			self._node.network.unsubscribe(self.on_pdo, self._cob_id_tx & 0x1FFFFFFF)
		else:
			self._node.network.unsubscribe(self.on_pdo, self._cob_id_tx & 0x7FF)
		
		Service.detach(self)
	
	def on_pdo(self, message):
		if not message.is_remote_frame:
			return
		if message.is_extended_id != bool(self._cob_id_tx & (1 << 29)):
			return
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
