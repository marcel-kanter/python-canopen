import struct
import can

from canopen.node.service import Service


class EMCYProducer(Service):
	""" ECMYProducer
	
	This class is an implementation of an EMCY producer.
	"""
	def __init__(self, node):
		""" Initializes the service
		
		:param node: The node, to which this service belongs to.
			Must be of type canopen.node.Node
		
		:raises: TypeError
		"""
		Service.__init__(self, node)
		self._cob_id_emcy = None
	
	def attach(self, cob_id_emcy = None):
		""" Attach handler. Must be called when the node gets attached to the network.
		
		:param cob_id_emcy: The COB ID for the EMCY service, used for the CAN ID of the EMCY messages to be sent.
			Bit 29 selects whether an extended frame is used. The CAN ID is masked out of the lowest 11 or 29 bits.
			It defaults to 0x80 + node.id if is omitted or None.
		"""
		if cob_id_emcy == None:
			cob_id_emcy = 0x80 + self._node.id
		if cob_id_emcy < 0 or cob_id_emcy > 0xFFFFFFFF:
			raise ValueError()
		if self.is_attached():
			self.detach()
		
		self._cob_id_emcy = cob_id_emcy
	
	def detach(self):
		""" Detach handler. Must be called when the node gets detached from the network.
		Raises RuntimeError if not attached.
		
		:raises: RuntimeError
		"""
		if not self.is_attached():
			raise RuntimeError()
		
		self._cob_id_emcy = None
	
	def is_attached(self):
		""" Returns True if the service is attached.
		"""
		return self._cob_id_emcy != None
	
	def send(self, error_code, error_register, data = None):
		""" Sends an emcy message on the bus. """
		if error_code < 0 or error_code > 0xFFFF:
			raise ValueError()
		if error_register < 0 or error_register > 0xFF:
			raise ValueError()
		if data == None:
			data = b""
		if len(data) > 5:
			raise ValueError()
		
		d = struct.pack("<HB5s", error_code, error_register, data)
		if self._cob_id_emcy & (1 << 29):
			message = can.Message(arbitration_id = self._cob_id_emcy & 0x1FFFFFFF, is_extended_id = True, data = d)
		else:
			message = can.Message(arbitration_id = self._cob_id_emcy & 0x7FF, is_extended_id = False, data = d)
		self._node.network.send(message)
