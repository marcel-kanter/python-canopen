import can
import canopen.node
from canopen.node.service.sync import SYNCConsumer


class LocalPDOProducer(SYNCConsumer):
	""" LocalPDOProducer
	
	Callbacks
	"sync": ("sync", service, counter)
	"rtr": ("rtr", service)
	"""
	def __init__(self, transmission_type = 0):
		if int(transmission_type) < 0 or (int(transmission_type) > 240 and int(transmission_type) < 252) or int(transmission_type) > 255:
			raise ValueError()
		
		SYNCConsumer.__init__(self)
		
		self._callbacks["rtr"] = []
		self._transmission_type = int(transmission_type)
		self._data = None
	
	def attach(self, node, cob_id_tx = None, cob_id_sync = None):
		""" Attaches the ``LocalPDOProducer`` to a ``Node``. It does NOT add or assign this ``LocalPDOProducer`` to the ``Node``.
		:param node: A canopen.Node, to which the service should be attached to.
		:param cob_id_tx: The COB ID for the PDO service, used for the CAN ID of the PDO messages to be sent.
			Bit 29 selects whether an extended frame is used. The CAN ID is masked out of the lowest 11 or 29 bits.
			If it is omitted or None is passed, the value defaults to 0x180 + node.id .
		:param cob_id_sync: The COB ID for the PDO service, used for the CAN ID of the SYNC messages to be received.
			Bit 29 selects whether an extended frame is used. The CAN ID is masked out of the lowest 11 or 29 bits.
			If it is omitted or None is passed, the value defaults to 0x80. """
		if not isinstance(node, canopen.node.Node):
			raise TypeError()
		if cob_id_tx == None:
			cob_id_tx = 0x180 + node.id
		if cob_id_tx < 0 or cob_id_tx > 0xFFFFFFFF:
			raise ValueError()
		
		SYNCConsumer.attach(self, node, cob_id_sync)
		self._cob_id_tx = cob_id_tx
		
		if self._cob_id_tx & (1 << 29):
			self._node.network.subscribe(self.on_pdo, self._cob_id_tx & 0x1FFFFFFF)
		else:
			self._node.network.subscribe(self.on_pdo, self._cob_id_tx & 0x7FF)
		
	def detach(self):
		""" Detaches the ``LocalPDOProducer`` from the ``Node``. It does NOT remove or delete the ``LocalPDOProducer`` from the ``Node``. """
		if not self.is_attached():
			raise RuntimeError()
		
		if self._cob_id_tx & (1 << 29):
			self._node.network.unsubscribe(self.on_pdo, self._cob_id_tx & 0x1FFFFFFF)
		else:
			self._node.network.unsubscribe(self.on_pdo, self._cob_id_tx & 0x7FF)
		
		SYNCConsumer.detach(self)
	
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
