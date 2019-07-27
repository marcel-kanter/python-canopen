import canopen.objectdictionary
from .variable import Variable


class DefType(Variable):
	def __init__(self, node, entry):
		if not isinstance(node, canopen.Node):
			raise TypeError()
		if not isinstance(entry, canopen.objectdictionary.DefType):
			raise TypeError()
		self._node = node
		self._entry = entry
	
	@property
	def object_type(self):
		return self._entry.object_type
