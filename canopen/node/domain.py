import canopen.objectdictionary
from .variable import Variable


class Domain(Variable):
	def __init__(self, node, entry):
		if not isinstance(node, canopen.Node):
			raise TypeError()
		if not isinstance(entry, canopen.objectdictionary.Domain):
			raise TypeError()
		self._node = node
		self._entry = entry
