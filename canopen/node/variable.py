import canopen.objectdictionary


class Variable(object):
	def __init__(self, node, entry):
		if not isinstance(node, canopen.Node):
			raise TypeError()
		if not isinstance(entry, canopen.objectdictionary.Variable):
			raise TypeError()
		self._node = node
		self._entry = entry
	
	@property
	def index(self):
		return self._entry.index
	
	@property
	def name(self):
		return self._entry.name
	
	@property
	def subindex(self):
		return self._entry.subindex
	
	@property
	def data_type(self):
		return self._entry.data_type
	
	@property
	def access_type(self):
		return self._entry.access_type
