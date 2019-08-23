import struct
import can
from canopen.node.service import Service


class EMCYProducer(Service):
	def __init__(self):
		Service.__init__(self)
	
	def attach(self, node):
		""" Attaches the ``EMCYProducer`` to a ``Node``. It does NOT add or assign this ``EMCYProducer`` to the ``Node``. """
		Service.attach(self, node)
		self._identifier_tx = 0x80 + self._node.id
	
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
		message = can.Message(arbitration_id = self._identifier_tx, is_extended_id = False, data = d)
		self._node.network.send(message)
