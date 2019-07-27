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
	
	@property
	def object_type(self):
		return self._entry.object_type
