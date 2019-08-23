import can
import canopen.objectdictionary
from canopen.node.service import Service
from canopen.objectdictionary import Variable


class TIMEProducer(Service):
	
	_helper_variable = Variable("helper", 0, 0, canopen.objectdictionary.TIME_OF_DAY)
	
	def __init__(self):
		Service.__init__(self)
	
	def attach(self, node, cob_id_time = None):
		""" Attaches the ``TIMEProducer`` to a ``Node``. It does NOT add or assign this ``TIMEProducer`` to the ``Node``. """
		if cob_id_time == None:
			cob_id_time = 0x100
		if cob_id_time < 0 or cob_id_time > 0xFFFFFFFF:
			raise ValueError()
		
		Service.attach(self, node)
		self._cob_id_time = cob_id_time
	
	def send(self, t):
		""" Sends a TIME message on the bus."""
		d = self._helper_variable.encode(t)
		if self._cob_id_time & (1 << 29):
			message = can.Message(arbitration_id = self._cob_id_time & 0x1FFFFFFF, is_extended_id = True, data = d)
		else:
			message = can.Message(arbitration_id = self._cob_id_time & 0x7FF, is_extended_id = False, data = d)
		self._node.network.send(message)
