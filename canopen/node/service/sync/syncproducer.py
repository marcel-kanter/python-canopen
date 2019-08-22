import can
import struct
from canopen.node.service import Service


class SYNCProducer(Service):
	def __init__(self):
		Service.__init__(self)
	
	def attach(self, node, cob_id_sync = None):
		""" Attaches the ``SYNCProducer`` to a ``Node``. It does NOT append or assign this ``SYNCProducer`` to the ``Node``. """
		if cob_id_sync == None:
			cob_id_sync = 0x80
		if cob_id_sync < 0 or cob_id_sync > 0xFFFFFFFF:
			raise ValueError()
		
		Service.attach(self, node)
		self._cob_id_sync = cob_id_sync
	
	def send(self, counter = None):
		""" Sends a SYNC message on the bus. If counter is None, no data is used in the SYNC message."""
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
