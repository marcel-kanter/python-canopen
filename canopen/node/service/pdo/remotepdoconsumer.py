import can
import canopen.node
from canopen.node.service import Service


class RemotePDOConsumer(Service):
	def __init__(self, transmission_type = 0):
		if int(transmission_type) < 0 or (int(transmission_type) > 240 and int(transmission_type) < 254) or int(transmission_type) > 255:
			raise ValueError()
		
		Service.__init__(self)
		self._transmission_type = int(transmission_type)
		self._data = None
	
	def attach(self, node, cob_id_tx = None):
		""" Attaches the ``RemotePDOConsumer`` to a ``Node``. It does NOT add or assign this ``RemotePDOConsumer`` to the ``Node``.
		:param node: A canopen.Node, to which the service should be attached to.
		:param cob_id_tx: The COB ID for the PDO service, used for the CAN ID of the PDO messages to be sent.
			Bit 29 selects whether an extended frame is used. The CAN ID is masked out of the lowest 11 or 29 bits.
			If it is omitted or None is passed, the value defaults to 0x180 + node.id ."""
		if not isinstance(node, canopen.node.Node):
			raise TypeError()
		if cob_id_tx == None:
			cob_id_tx = 0x200 + node.id
		if cob_id_tx < 0 or cob_id_tx > 0xFFFFFFFF:
			raise ValueError()
		
		Service.attach(self, node)
		self._cob_id_tx = cob_id_tx
		
	def detach(self):
		""" Detaches the ``RemotePDOConsumer`` from the ``Node``. It does NOT remove or delete the ``RemotePDOConsumer`` from the ``Node``. """
		Service.detach(self)
	
	def send(self):
		if self._data == None:
			raise RuntimeError()
		
		if self._cob_id_tx & (1 << 29):
			message = can.Message(arbitration_id = self._cob_id_tx & 0x1FFFFFFF, is_extended_id = True, data = self._data)
		else:
			message = can.Message(arbitration_id = self._cob_id_tx & 0x7FF, is_extended_id = False, data = self._data)
		self._node.network.send(message)
	
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
