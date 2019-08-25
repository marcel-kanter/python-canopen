import struct
import canopen.node
from canopen.node.service import Service


class EMCYConsumer(Service):
	""" EMCY consumer
	
	This class is an implementation of a DS301 EMCY consumer. 
	"""
	def __init__(self):
		Service.__init__(self)
		self._callbacks = {"emcy": []}
	
	def attach(self, node, cob_id_emcy = None):
		""" Attaches the ``EMCYConsumer`` to a ``Node``. It does NOT add or assign this ``EMCYConsumer`` to the ``Node``. """
		if not isinstance(node, canopen.node.Node):
			raise TypeError()
		if cob_id_emcy == None:
			cob_id_emcy = 0x80 + node.id
		if cob_id_emcy < 0 or cob_id_emcy > 0xFFFFFFFF:
			raise ValueError()
		
		Service.attach(self, node)
		self._cob_id_emcy = cob_id_emcy
		
		if self._cob_id_emcy & (1 << 29):
			self._node.network.subscribe(self.on_emcy, self._cob_id_emcy & 0x1FFFFFFF)
		else:
			self._node.network.subscribe(self.on_emcy, self._cob_id_emcy & 0x7FF)
	
	def detach(self):
		""" Detaches the ``EMCYConsumer`` from the ``Node``. It does NOT remove or delete the ``EMCYConsumer`` from the ``Node``. """
		if self._node == None:
			raise RuntimeError()
		if self._cob_id_emcy & (1 << 29):
			self._node.network.unsubscribe(self.on_emcy, self._cob_id_emcy & 0x1FFFFFFF)
		else:
			self._node.network.unsubscribe(self.on_emcy, self._cob_id_emcy & 0x7FF)
		Service.detach(self)
		
	def on_emcy(self, message):
		if message.is_extended_id != bool(self._cob_id_emcy & (1 << 29)):
			return
		
		error_code, error_register, data = struct.unpack("<HB5s", message.data)
		
		self.notify("emcy", self, error_code, error_register, data)
