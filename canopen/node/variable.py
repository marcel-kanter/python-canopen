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
		return self._entry._index
	
	@property
	def name(self):
		return self._entry._name
	
	@property
	def subindex(self):
		return self._entry._subindex
	
	@property
	def data_type(self):
		return self._entry._data_type
	
	@property
	def access_type(self):
		return self._entry._access_type
