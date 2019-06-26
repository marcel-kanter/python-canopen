import canopen.objectdictionary
from .record import Record


class DefStruct(Record):
	def __init__(self, node, entry):
		if not isinstance(node, canopen.Node):
			raise TypeError()
		if not isinstance(entry, canopen.objectdictionary.DefStruct):
			raise TypeError()
		self._node = node
		self._entry = entry
