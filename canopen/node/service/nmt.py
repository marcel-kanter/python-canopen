import canopen.node


class NMTSlave(object):
	def __init__(self):
		self._node = None
		self._state = 0
	
	def attach(self, node):
		if not isinstance(node, canopen.node.Node):
			raise TypeError()
		if self._node == node:
			raise ValueError()
		if self._node != None:
			self.detach()
		
		self._node = node
	
	def detach(self):
		self._node = None
	
	@property
	def state(self):
		return self._state
