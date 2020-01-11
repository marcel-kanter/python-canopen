import can
import struct

from canopen.node.service import Service


class SYNCProducer(Service):
	""" SYNCProducer
	
	This class is an implementation of a SYNC producer.
	"""
	
	def __init__(self, node):
		""" Initializes the service
		
		:param node: The node, to which this service belongs to. Must be of type canopen.node.Node
		
		:raises: TypeError
		"""
		Service.__init__(self, node)
		self._cob_id_sync = None
	
	def attach(self, cob_id_sync = None):
		""" Attach handler. Must be called when the node gets attached to the network.
		
		:param cob_id_sync: The COB ID for the SYNC service. Bit 29 selects whether an extended frame is used. The CAN ID is masked out of the lowest 11 or 29 bits.
			If it is omitted or None is passed, the value defaults to 0x80.
		
		:raises: ValueError
		"""
		if cob_id_sync == None:
			cob_id_sync = 0x80
		if cob_id_sync < 0 or cob_id_sync > 0xFFFFFFFF:
			raise ValueError()
		if self.is_attached():
			self.detach()
		
		self._cob_id_sync = int(cob_id_sync)
	
	def detach(self):
		""" Detach handler. Must be called when the node gets detached from the network.
		"""
		if not self.is_attached():
			raise RuntimeError()
		
		self._cob_id_sync = None
		
	def is_attached(self):
		""" Returns True if the service is attached.
		"""
		return self._cob_id_sync != None
	
	def send(self, counter = None):
		""" Sends a SYNC message on the bus. If counter is None, no data is used in the SYNC message.
		
		:param counter: The counter value to send with the SYNC message. If None, the counter value is omitted from the SYNC message.
		"""
		if self._cob_id_sync & (1 << 29):
			message = can.Message(arbitration_id = self._cob_id_sync & 0x1FFFFFFF, is_extended_id = True)
		else:
			message = can.Message(arbitration_id = self._cob_id_sync & 0x7FF, is_extended_id = False)
			
		if counter == None:
			message.dlc = 0
		else:
			d = struct.pack("<B", int(counter))
			message.data = d
		self._node.network.send(message)
