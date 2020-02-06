import threading

from canopen.node.service.sync import SYNCConsumer


class PDOConsumer(SYNCConsumer):
	""" PDOConsumer
	
	Callbacks
	"sync": ("sync", service, counter)
	"pdo": ("pdo", service)
	"""
	def __init__(self, node, transmission_type = 0):
		""" Initializes the service
		
		:param node: The node, to which this service belongs to. Must be of type canopen.node.Node
		
		:param transmission_type:
		
		:raises: TypeError
		"""
		if int(transmission_type) < 0 or (int(transmission_type) > 240 and int(transmission_type) < 254) or int(transmission_type) > 255:
			raise ValueError()
		
		SYNCConsumer.__init__(self, node)
		self.add_event("pdo")
		self._cob_id_rx = None

		self._transmission_type = int(transmission_type)
		self._data = None
		self._pdo_condition = threading.Condition()
	
	def attach(self, cob_id_rx = None, cob_id_sync = None):
		""" Attach handler. Must be called when the node gets attached to the network.
		
		:param cob_id_rx: The COB ID for the PDO service, used for the CAN ID of the PDO messages to be received.
			Bit 29 selects whether an extended frame is used. The CAN ID is masked out of the lowest 11 or 29 bits.
			It defaults to 0x200 + node.id if it is omitted.
		
		:param cob_id_sync: The COB ID for the PDO service, used for the CAN ID of the SYNC messages to be received.
			Bit 29 selects whether an extended frame is used. The CAN ID is masked out of the lowest 11 or 29 bits.
			It defaults to 0x80 if it is omitted.
		
		:raises: ValueError
		"""
		if cob_id_rx == None:
			cob_id_rx = 0x200 + self._node.id
		if cob_id_rx < 0 or cob_id_rx > 0xFFFFFFFF:
			raise ValueError()
		
		SYNCConsumer.attach(self, cob_id_sync)
		
		if cob_id_rx & (1 << 29):
			self._node.network.subscribe(self.on_pdo, cob_id_rx & 0x1FFFFFFF)
		else:
			self._node.network.subscribe(self.on_pdo, cob_id_rx & 0x7FF)
		
		self._cob_id_rx = int(cob_id_rx)
	
	def detach(self):
		""" Detach handler. Must be called when the node gets detached from the network.
		"""
		SYNCConsumer.detach(self)
		
		if self._cob_id_rx & (1 << 29):
			self._node.network.unsubscribe(self.on_pdo, self._cob_id_rx & 0x1FFFFFFF)
		else:
			self._node.network.unsubscribe(self.on_pdo, self._cob_id_rx & 0x7FF)
		
		self._cob_id_rx = None
	
	def is_attached(self):
		""" Returns True if the service is attached.
		"""
		return self._cob_id_rx != None
	
	def wait_for_pdo(self, timeout = None):
		with self._pdo_condition:
			gotit = self._pdo_condition.wait(timeout)
		return gotit
	
	def on_pdo(self, message):
		if message.is_remote_frame:
			return
		if message.is_extended_id != bool(self._cob_id_rx & (1 << 29)):
			return
		self._data = message.data
		self.notify("pdo", self)
		with self._pdo_condition:
			self._pdo_condition.notify_all()
	
	@property
	def data(self):
		return self._data
	
	@data.setter
	def data(self, data):
		self._data = data
	
	@property
	def transmission_type(self):
		return self._transmission_type
	
	@transmission_type.setter
	def transmission_type(self, value):
		x = int(value)
		if x < 0 or (x > 240 and x < 254) or x > 255:
			raise ValueError()
		self._transmission_type = x
