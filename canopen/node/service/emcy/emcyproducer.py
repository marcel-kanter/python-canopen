import struct
import can
import canopen.node
from canopen.node.service import Service


class EMCYProducer(Service):
	def __init__(self):
		Service.__init__(self)
	
	def attach(self, node, cob_id_emcy = None):
		""" Attaches the ``EMCYProducer`` to a ``Node``. It does NOT add or assign this ``EMCYProducer`` to the ``Node``.
		:param node: A canopen.Node, to which the service should be attached to.
		:param cob_id_emcy: The COB ID for the EMCY service, used for the CAN ID of the EMCY messages to be sent.
			Bit 29 selects whether an extended frame is used. The CAN ID is masked out of the lowest 11 or 29 bits.
			If it is omitted or None is passed, the value defaults to 0x80 + node.id . """
		if not isinstance(node, canopen.node.Node):
			raise TypeError()
		if cob_id_emcy == None:
			cob_id_emcy = 0x80 + node.id
		if cob_id_emcy < 0 or cob_id_emcy > 0xFFFFFFFF:
			raise ValueError()
		
		Service.attach(self, node)
		self._cob_id_emcy = cob_id_emcy
	
	def detach(self):
		""" Detaches the ``EMCYProducer`` from the ``Node``. It does NOT remove or delete the ``EMCYProducer`` from the ``Node``. """
		Service.detach(self)
	
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
