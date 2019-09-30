import struct
import canopen.node
from canopen.node.service import Service


class EMCYConsumer(Service):
	""" EMCYConsumer
	
	This class is an implementation of an EMCY consumer.
	
	Callbacks
	emcy
	"""
	def __init__(self):
		Service.__init__(self)
		self._callbacks = {"emcy": []}
	
	def attach(self, node, cob_id_emcy = None):
		""" Attaches the ``EMCYConsumer`` to a ``Node``. It does NOT add or assign this ``EMCYConsumer`` to the ``Node``.
		:param node: A canopen.Node, to which the service should be attached to.
		:param cob_id_emcy: The COB ID for the EMCY service, used for the CAN ID of the EMCY messages to be recevied.
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
