import canopen.node


class Service(object):
	""" Service
	
	This class is the base class for all services of a node.
	"""
	def __init__(self):
		self._node = None
	
	def attach(self, node):
		""" Attaches the service to a node. It does NOT append or assign this service to the node. """
		if not isinstance(node, canopen.node.Node):
			raise TypeError()
		if self._node == node:
			raise ValueError()
		if self._node != None:
			self.detach()
		
		self._node = node
	
	def detach(self):
		""" Detaches the service from the node. It does NOT remove or delete the service from the node. """
		if self._node == None:
			raise RuntimeError()
		
		self._node = None
