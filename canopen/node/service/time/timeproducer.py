import can
import canopen.objectdictionary
from canopen.node.service import Service
from canopen.objectdictionary import Variable


class TIMEProducer(Service):
	""" TIMEProducer
	
	This class is an implementation of a TIME producer.
	"""
	
	_helper_variable = Variable("helper", 0, 0, canopen.objectdictionary.TIME_OF_DAY)
	
	def __init__(self):
		Service.__init__(self)
	
	def attach(self, node, cob_id_time = None):
		""" Attaches the ``TIMEProducer`` to a ``Node``. It does NOT add or assign this ``TIMEProducer`` to the ``Node``.
		:param node: A canopen.Node, to which the service should be attached to.
		:param cob_id_time: The COB ID for the TIME service. Bit 29 selects whether an extended frame is used. The CAN ID is masked out of the lowest 11 or 29 bits.
			If it is omitted or None is passed, the value defaults to 0x100. """
		if cob_id_time == None:
			cob_id_time = 0x100
		if cob_id_time < 0 or cob_id_time > 0xFFFFFFFF:
			raise ValueError()
		
		Service.attach(self, node)
		self._cob_id_time = cob_id_time
	
	def send(self, t):
		""" Sends a TIME message on the bus.
		:param t: The the stamp to send. The value is encoded like a Variable of data type TIME_OF_DAY. Values before the canopen epoch are not allowed."""
		d = self._helper_variable.encode(t)
		if self._cob_id_time & (1 << 29):
			message = can.Message(arbitration_id = self._cob_id_time & 0x1FFFFFFF, is_extended_id = True, data = d)
		else:
			message = can.Message(arbitration_id = self._cob_id_time & 0x7FF, is_extended_id = False, data = d)
		self._node.network.send(message)
