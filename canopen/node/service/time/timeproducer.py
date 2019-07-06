import can
import canopen.objectdictionary
from canopen.node.service import Service
from canopen.objectdictionary import Variable


class TIMEProducer(Service):
	
	_helper_variable = Variable("helper", 0, 0, canopen.objectdictionary.TIME_OF_DAY)
	
	def __init__(self):
		Service.__init__(self)
	
	def attach(self, node):
		Service.attach(self, node)
		self._identifier = 0x100
	
	def send(self, t):
		""" Sends a TIME message on the bus."""
		d = self._helper_variable.encode(t)
		message = can.Message(arbitration_id = self._identifier, is_extended_id = False, data = d)
		self._node.network.send(message)
