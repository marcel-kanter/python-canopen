import canopen.node
from canopen.node.service import Service


class SRDOConsumer(Service):
	""" SRDOConsumer
	"""
	def __init__(self):
		Service.__init__(self)
		self._normal_data = None
		self._complement_data = None
	
	def attach(self, node, cob_id_1 = None, cob_id_2 = None):
		""" Attaches the ``SRDOConsumer`` to a ``Node``. It does NOT add or assign this ``SRDOConsumer`` to the ``Node``.
		:param node: A canopen.Node, to which the service should be attached to.
		:param cob_id_1: The COB ID for the SRDO service, used for the CAN ID of the normal data frames.
			DS304 only allows odd values in the range 0x101 to 0x17F. This service supports the whole COB ID range. 
			Bit 29 selects whether an extended frame is used. The CAN ID is masked out of the lowest 11 or 29 bits.
			If it is omitted or None is passed, the value defaults to 0xFF + 2 * node.id .
		:param cob_id_2: The COB ID for the SRDO service, used for the CAN ID of the complement data frames.
			DS304 only allows even values in the range 0x102 to 0x180. This service supports the whole COB ID range.
			Bit 29 selects whether an extended frame is used. The CAN ID is masked out of the lowest 11 or 29 bits.
			If it is omitted or None is passed, the value defaults to 0x100 + 2 * node.id . """
		if not isinstance(node, canopen.node.Node):
			raise TypeError()
		if cob_id_1 == None:
			cob_id_1 = 0xFF + 2 * node.id
		if cob_id_1 < 0x0 or cob_id_1 > 0xFFFFFFFF:
			raise ValueError()
		if cob_id_2 == None:
			cob_id_2 = 0x100 + 2 * node.id
		if cob_id_2 < 0x0 or cob_id_2 > 0xFFFFFFFF:
			raise ValueError()
		
		Service.attach(self, node)
		self._cob_id_1 = cob_id_1
		self._cob_id_2 = cob_id_2
		
		if self._cob_id_1 & (1 << 29):
			self._node.network.subscribe(self.on_message1, self._cob_id_1 & 0x1FFFFFFF)
		else:
			self._node.network.subscribe(self.on_message1, self._cob_id_1 & 0x7FF)
		if self._cob_id_2 & (1 << 29):
			self._node.network.subscribe(self.on_message2, self._cob_id_2 & 0x1FFFFFFF)
		else:
			self._node.network.subscribe(self.on_message2, self._cob_id_2 & 0x7FF)
	
	def detach(self):
		if not self.is_attached():
			raise RuntimeError()
		
		if self._cob_id_1 & (1 << 29):
			self._node.network.unsubscribe(self.on_message1, self._cob_id_1 & 0x1FFFFFFF)
		else:
			self._node.network.unsubscribe(self.on_message1, self._cob_id_1 & 0x7FF)
		if self._cob_id_2 & (1 << 29):
			self._node.network.unsubscribe(self.on_message2, self._cob_id_2 & 0x1FFFFFFF)
		else:
			self._node.network.unsubscribe(self.on_message2, self._cob_id_2 & 0x7FF)

		Service.detach(self)
	
	def on_message1(self, message):
		""" Message handler for incoming SRDO messages with normal data. """
		if message.is_remote_frame:
			return
		if message.is_extended_id != bool(self._cob_id_1 & (1 << 29)):
			return

	def on_message2(self, message):
		""" Message handler for incoming SRDO messages with complement data. """
		if message.is_remote_frame:
			return
		if message.is_extended_id != bool(self._cob_id_2 & (1 << 29)):
			return
	
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
