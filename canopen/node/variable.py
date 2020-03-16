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
	def value(self):
		return self._node.get_data(self._entry.index, self._entry.subindex)
	
	@value.setter
	def value(self, x):
		self._node.set_data(self._entry.index, self._entry.subindex, x)
	
	@property
	def object_type(self):
		return self._entry.object_type
	
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
	
	@property
	def default_value(self):
		return self._entry.default_value
	
	@property
	def description(self):
		return self._entry.description
	
	@property
	def size(self):
		return self._entry.size
	
	@property
	def pdo_mapping(self):
		return self._entry.pdo_mapping
	
	@property
	def srdo_mapping(self):
		return self._entry.srdo_mapping
