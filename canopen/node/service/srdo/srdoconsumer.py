from canopen.node.service.sync import SYNCConsumer
from canopen.node.service.objectmapping import ObjectMapping


class SRDOConsumer(SYNCConsumer):
	""" SRDOConsumer
	
	Callbacks
	"sync": ("sync", service, counter)
	"""
	def __init__(self, node):
		""" Initializes the service
		
		:param node: The node, to which this service belongs to. Must be of type canopen.node.Node
		
		:raises: TypeError
		"""
		SYNCConsumer.__init__(self, node)
		self._cob_id_1 = None
		self._cob_id_2 = None
		
		self._normal_data = None
		self._complement_data = None
		
		self.mapping = ObjectMapping(self)
	
	def attach(self, cob_id_1 = None, cob_id_2 = None, cob_id_sync = None):
		""" Attach handler. Must be called when the node gets attached to the network.
		
		:param cob_id_1: The COB ID for the SRDO service, used for the CAN ID of the normal data frames.
			DS304 only allows odd values in the range 0x101 to 0x17F. This service supports the whole COB ID range. 
			Bit 29 selects whether an extended frame is used. The CAN ID is masked out of the lowest 11 or 29 bits.
			If it is omitted or None is passed, the value defaults to 0xFF + 2 * node.id .

		:param cob_id_2: The COB ID for the SRDO service, used for the CAN ID of the complement data frames.
			DS304 only allows even values in the range 0x102 to 0x180. This service supports the whole COB ID range.
			Bit 29 selects whether an extended frame is used. The CAN ID is masked out of the lowest 11 or 29 bits.
			If it is omitted or None is passed, the value defaults to 0x100 + 2 * node.id .

		:param cob_id_sync: The COB ID for the PDO service, used for the CAN ID of the SYNC messages to be received.
			Bit 29 selects whether an extended frame is used. The CAN ID is masked out of the lowest 11 or 29 bits.
			If it is omitted or None is passed, the value defaults to 0x80.
		
		:raises: ValueError
		"""
		if cob_id_1 == None:
			cob_id_1 = 0xFF + 2 * self._node.id
		if cob_id_1 < 0x0 or cob_id_1 > 0xFFFFFFFF:
			raise ValueError()
		if cob_id_2 == None:
			cob_id_2 = 0x100 + 2 * self._node.id
		if cob_id_2 < 0x0 or cob_id_2 > 0xFFFFFFFF:
			raise ValueError()
		
		SYNCConsumer.attach(self, cob_id_sync)
		
		if cob_id_1 & (1 << 29):
			self._node.network.subscribe(self.on_message1, cob_id_1 & 0x1FFFFFFF)
		else:
			self._node.network.subscribe(self.on_message1, cob_id_1 & 0x7FF)
		if cob_id_2 & (1 << 29):
			self._node.network.subscribe(self.on_message2, cob_id_2 & 0x1FFFFFFF)
		else:
			self._node.network.subscribe(self.on_message2, cob_id_2 & 0x7FF)
		
		self._cob_id_1 = int(cob_id_1)
		self._cob_id_2 = int(cob_id_2)
	
	def detach(self):
		""" Detach handler. Must be called when the node gets detached from the network.
		"""
		SYNCConsumer.detach(self)
		
		if self._cob_id_1 & (1 << 29):
			self._node.network.unsubscribe(self.on_message1, self._cob_id_1 & 0x1FFFFFFF)
		else:
			self._node.network.unsubscribe(self.on_message1, self._cob_id_1 & 0x7FF)
		if self._cob_id_2 & (1 << 29):
			self._node.network.unsubscribe(self.on_message2, self._cob_id_2 & 0x1FFFFFFF)
		else:
			self._node.network.unsubscribe(self.on_message2, self._cob_id_2 & 0x7FF)
	
		self._cob_id_1 = None
		self._cob_id_2 = None
	
	def is_attached(self):
		""" Returns True if the service is attached.
		"""
		return self._cob_id_1 != None
	
	def on_message1(self, message):
		""" Message handler for incoming SRDO messages with normal data. """
		if not self._enabled:
			return
		if message.is_remote_frame:
			return
		if message.is_extended_id != bool(self._cob_id_1 & (1 << 29)):
			return
		
		self._normal_data = message.data
	
	def on_message2(self, message):
		""" Message handler for incoming SRDO messages with complement data. """
		if not self._enabled:
			return
		if message.is_remote_frame:
			return
		if message.is_extended_id != bool(self._cob_id_2 & (1 << 29)):
			return
		
		self._complement_data = message.data
	
	@property
	def normal_data(self):
		return self._normal_data
	
	@normal_data.setter
	def normal_data(self, data):
		self._normal_data = data
	
	@property
	def complement_data(self):
		return self._complement_data
	
	@complement_data.setter
	def complement_data(self, data):
		self._complement_data = data
