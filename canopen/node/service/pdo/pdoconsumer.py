import canopen.node
from canopen.node.service.sync import SYNCConsumer


class PDOConsumer(SYNCConsumer):
	""" PDOConsumer
	
	Callbacks
	"sync": ("sync", service, counter)
	"pdo": ("pdo", service)
	"""
	def __init__(self):
		SYNCConsumer.__init__(self)
		self._callbacks["pdo"] = []
		self._data = None
	
	def attach(self, node, cob_id_rx = None, cob_id_sync = None):
		""" Attaches the ``PDOConsumer`` to a ``Node``. It does NOT add or assign this ``PDOConsumer`` to the ``Node``.
		:param node: A canopen.Node, to which the service should be attached to.
		:param cob_id_rx: The COB ID for the PDO service, used for the CAN ID of the PDO messages to be received.
			Bit 29 selects whether an extended frame is used. The CAN ID is masked out of the lowest 11 or 29 bits.
			If it is omitted or None is passed, the value defaults to 0x200 + node.id.
		:param cob_id_sync: The COB ID for the PDO service, used for the CAN ID of the SYNC messages to be received.
			Bit 29 selects whether an extended frame is used. The CAN ID is masked out of the lowest 11 or 29 bits.
			If it is omitted or None is passed, the value defaults to 0x80. """
		if not isinstance(node, canopen.node.Node):
			raise TypeError()
		if cob_id_rx == None:
			cob_id_rx = 0x200 + node.id
		if cob_id_rx < 0 or cob_id_rx > 0xFFFFFFFF:
			raise ValueError()
		
		SYNCConsumer.attach(self, node, cob_id_sync)
		self._cob_id_rx = cob_id_rx
		
		if self._cob_id_rx & (1 << 29):
			self._node.network.subscribe(self.on_pdo, self._cob_id_rx & 0x1FFFFFFF)
		else:
			self._node.network.subscribe(self.on_pdo, self._cob_id_rx & 0x7FF)
	
	def detach(self):
		""" Detaches the ``PDOConsumer`` from the ``Node``. It does NOT remove or delete the ``PDOConsumer`` from the ``Node``. """
		if self._node == None:
			raise RuntimeError()
		
		if self._cob_id_rx & (1 << 29):
			self._node.network.unsubscribe(self.on_pdo, self._cob_id_rx & 0x1FFFFFFF)
		else:
			self._node.network.unsubscribe(self.on_pdo, self._cob_id_rx & 0x7FF)
		
		SYNCConsumer.detach(self)
	
	def on_pdo(self, message):
		if message.is_remote_frame:
			return
		if message.is_extended_id != bool(self._cob_id_rx & (1 << 29)):
			return
		self._data = message.data
		self.notify("pdo", self)
	
	@property
	def data(self):
		return self._data
	
	@data.setter
	def data(self, data):
		self._data = data
