from canopen.node.service import Service


class NMTMaster(Service):
	""" NMTMaster service.
	
	This class is an implementation of the NMT master. The nmt state of the node can be accessed by the state property.
	"""
	def __init__(self):
		Service.__init__(self)
		self._state = 0

	def attach(self, node):
		Service.attach(self, node)
		self._state = 0
	
	def detach(self):
		if self._node == None:
			raise RuntimeError()
		
		Service.detach(self)
	
	@property
	def state(self):
		return self._state
