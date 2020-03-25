import struct

from canopen.node.service import Service


class EMCYConsumer(Service):
	""" EMCYConsumer
	
	This class is an implementation of an EMCY consumer.
	
	Callbacks
	"emcy": ("emcy", service, error_code, error_register, data)
	"""
	def __init__(self, node):
		""" Initializes the service
		
		:param node: The node, to which this service belongs to.
			Must be of type canopen.node.Node
		
		:raises: TypeError
		"""
		Service.__init__(self, node)
		self.add_event("emcy")
		self._cob_id_emcy = None
	
	def attach(self, cob_id_emcy = None):
		""" Attach handler. Must be called when the node gets attached to the network.
		
		:param cob_id_emcy: The COB ID for the EMCY service, used for the CAN ID of the EMCY messages to be recevied.
			Bit 29 selects whether an extended frame is used. The CAN ID is masked out of the lowest 11 or 29 bits.
			It defaults to 0x80 + node.id if it is omitted or None.
		
		:raises: ValueError
		"""
		if cob_id_emcy == None:
			cob_id_emcy = 0x80 + self._node.id
		if cob_id_emcy < 0 or cob_id_emcy > 0xFFFFFFFF:
			raise ValueError()
		if self.is_attached():
			self.detach()
		
		if cob_id_emcy & (1 << 29):
			self._node.network.subscribe(self.on_emcy, cob_id_emcy & 0x1FFFFFFF)
		else:
			self._node.network.subscribe(self.on_emcy, cob_id_emcy & 0x7FF)
		
		self._cob_id_emcy = int(cob_id_emcy)
	
	def detach(self):
		""" Detach handler. Must be called when the node gets detached from the network.
		Raises RuntimeError if not attached.
		
		:raises: RuntimeError
		"""
		if not self.is_attached():
			raise RuntimeError()
		
		if self._cob_id_emcy & (1 << 29):
			self._node.network.unsubscribe(self.on_emcy, self._cob_id_emcy & 0x1FFFFFFF)
		else:
			self._node.network.unsubscribe(self.on_emcy, self._cob_id_emcy & 0x7FF)
		
		self._cob_id_emcy = None
	
	def is_attached(self):
		""" Returns True if the service is attached.
		"""
		return self._cob_id_emcy != None
	
	def on_emcy(self, message):
		if not self._enabled:
			return
		if message.is_extended_id != bool(self._cob_id_emcy & (1 << 29)):
			return
		
		error_code, error_register, data = struct.unpack("<HB5s", message.data)
		
		self.notify("emcy", self, error_code, error_register, data)
