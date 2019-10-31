from .datatypes import UNSIGNED8, UNSIGNED16, UNSIGNED32
from .array import Array
from .variable import Variable


class DefStruct(Array):
	""" Representation of a DefStruct of an object dictionary.
	
	This class is the representation of a DefStruct of an object dictionary. It is a mutable auto-associative mapping and may contain zero or more variables.
	"""
	def __init__(self, name, index):
		Array.__init__(self, name, index, UNSIGNED16)
		self._object_type = 6
	
	def add(self, value):
		""" Adds a variable to the record. It may be accessed later by the name or the subindex. """
		if not isinstance(value, Variable):
			raise TypeError()
		# Allow objects with object type 7 (Variable) only. DefType and Domain are sub-classes of Variable and thus will pass the isinstance check.
		if value.object_type != 7:
			raise TypeError()
		if value.subindex == 0x00:
			if value.data_type != UNSIGNED8:
				raise ValueError()
		elif value.subindex == 0xFF:
			if value.data_type != UNSIGNED32:
				raise ValueError()
		else:
			if value.data_type != UNSIGNED16:
				raise ValueError()
		if value.access_type != "ro" and value.access_type != "const":
			raise ValueError()
		
		Array.add(self, value)
