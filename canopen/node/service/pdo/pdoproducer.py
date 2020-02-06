import can

from canopen.node.service.sync import SYNCConsumer
from canopen.node.service.objectmapping import ObjectMapping


class PDOProducer(SYNCConsumer):
	""" PDOProducer
	
	Callbacks
	"sync": ("sync", service, counter)
	"rtr": ("rtr", service)
	"""
	def __init__(self, node, transmission_type = 0):
		""" Initializes the service
		
		:param node: The node, to which this service belongs to. Must be of type canopen.node.Node
		
		:param transmission_type:
		
		:raises: TypeError
		"""
		if int(transmission_type) < 0 or (int(transmission_type) > 240 and int(transmission_type) < 252) or int(transmission_type) > 255:
			raise ValueError()
		
		SYNCConsumer.__init__(self, node)
		self.add_event("rtr")
		self._cob_id_tx = None
		
		self._transmission_type = int(transmission_type)
		self._data = None
		
		self.mapping = ObjectMapping(self)
	
	def attach(self, cob_id_tx = None, cob_id_sync = None):
		""" Attach handler. Must be called when the node gets attached to the network.
		
		:param cob_id_tx: The COB ID for the PDO service, used for the CAN ID of the PDO messages to be sent.
			Bit 29 selects whether an extended frame is used. The CAN ID is masked out of the lowest 11 or 29 bits.
			Ii defaults to 0x180 + node.id if it is omitted.

		:param cob_id_sync: The COB ID for the PDO service, used for the CAN ID of the SYNC messages to be received.
			Bit 29 selects whether an extended frame is used. The CAN ID is masked out of the lowest 11 or 29 bits.
			It defaults to 0x80 if it is omitted.
		"""
		if cob_id_tx == None:
			cob_id_tx = 0x180 + self._node.id
		if cob_id_tx < 0 or cob_id_tx > 0xFFFFFFFF:
			raise ValueError()
		
		SYNCConsumer.attach(self, cob_id_sync)
		
		if cob_id_tx & (1 << 29):
			self._node.network.subscribe(self.on_pdo, cob_id_tx & 0x1FFFFFFF)
		else:
			self._node.network.subscribe(self.on_pdo, cob_id_tx & 0x7FF)
			
		self._cob_id_tx = int(cob_id_tx)
		
	def detach(self):
		""" Detach handler. Must be called when the node gets detached from the network.
		"""
		SYNCConsumer.detach(self)
		
		if self._cob_id_tx & (1 << 29):
			self._node.network.unsubscribe(self.on_pdo, self._cob_id_tx & 0x1FFFFFFF)
		else:
			self._node.network.unsubscribe(self.on_pdo, self._cob_id_tx & 0x7FF)
		
		self._cob_id_tx = None
	
	def is_attached(self):
		""" Returns True if the service is attached.
		"""
		return self._cob_id_tx != None

	def send(self):
		if self._data == None:
			raise RuntimeError()
		
		if self._cob_id_tx & (1 << 29):
			message = can.Message(arbitration_id = self._cob_id_tx & 0x1FFFFFFF, is_extended_id = True, data = self._data)
		else:
			message = can.Message(arbitration_id = self._cob_id_tx & 0x7FF, is_extended_id = False, data = self._data)
		self._node.network.send(message)
	
	def on_pdo(self, message):
		if not message.is_remote_frame:
			return
		if message.is_extended_id != bool(self._cob_id_tx & (1 << 29)):
			return
		self.notify("rtr", self)
	
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
		if x < 0 or (x > 240 and x < 252) or x > 255:
			raise ValueError()
		self._transmission_type = x
