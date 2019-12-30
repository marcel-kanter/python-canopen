import struct
import threading
from canopen.node.service import Service


class SYNCConsumer(Service):
	""" SYNCConsumer
	
	This class is an implementation of a SYNC consumer.
	
	Callbacks
	"sync": ("sync", service, counter)
	"""
	
	def __init__(self):
		Service.__init__(self)
		self._callbacks = {"sync": []}
		self._sync_condition = threading.Condition()
	
	def attach(self, node, cob_id_sync = None):
		""" Attaches the ``SYNCConsumer`` to a ``Node``. It does NOT add or assign this ``SYNCConsumer`` to the ``Node``.
		:param node: A canopen.Node, to which the service should be attached to.
		:param cob_id_sync: The COB ID for the SYNC service. Bit 29 selects whether an extended frame is used. The CAN ID is masked out of the lowest 11 or 29 bits.
			If it is omitted or None is passed, the value defaults to 0x80. """
		if cob_id_sync == None:
			cob_id_sync = 0x80
		if cob_id_sync < 0 or cob_id_sync > 0xFFFFFFFF:
			raise ValueError()
		
		Service.attach(self, node)
		self._cob_id_sync = cob_id_sync
		
		if self._cob_id_sync & (1 << 29):
			self._node.network.subscribe(self.on_sync, self._cob_id_sync & 0x1FFFFFFF)
		else:
			self._node.network.subscribe(self.on_sync, self._cob_id_sync & 0x7FF)
	
	def detach(self):
		""" Detaches the ``SYNCConsumer`` from the ``Node``. It does NOT remove or delete the ``SYNCConsumer`` from the ``Node``. """
		if not self.is_attached():
			raise RuntimeError()
		if self._cob_id_sync & (1 << 29):
			self._node.network.unsubscribe(self.on_sync, self._cob_id_sync & 0x1FFFFFFF)
		else:
			self._node.network.unsubscribe(self.on_sync, self._cob_id_sync & 0x7FF)
		Service.detach(self)
	
	def on_sync(self, message):
		""" Message handler for incoming SYNC messages. """
		if message.is_remote_frame:
			return
		if message.is_extended_id != bool(self._cob_id_sync & (1 << 29)):
			return
		if message.dlc == 1:
			counter, = struct.unpack_from("<B", message.data)
		else:
			counter = None
		self.notify("sync", self, counter)
		with self._sync_condition:
			self._sync_condition.notify_all()
	
	def wait_for_sync(self, timeout = None):
		""" Wait until the reception of SYNC message or until a timeout occurs.
		
		When the timeout argument is present and not None, it should be a floating point number specifying a timeout for the operation in seconds (or fractions thereof).
		
		:param timeout: The time to wait in seconds, or ``None``
		
		:returns: True if the sync message was received, False if the timeout occured
		"""
		with self._sync_condition:
			gotit = self._sync_condition.wait(timeout)
		return gotit
