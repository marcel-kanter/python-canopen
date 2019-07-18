from canopen.node.service import Service


class PDOProducer(Service):
	def __init__(self):
		Service.__init__(self)
	
	def attach(self, node):
		""" Attaches the service to a node. It does NOT append or assign this service to the node. """
		Service.attach(self, node)
		self._identifier_tx = 0x180 + self._node.id
		
	def detach(self):
		""" Detaches the service from the node. It does NOT remove or delete the service from the node. """
		if self._node == None:
			raise RuntimeError()
		
		Service.detach(self)
