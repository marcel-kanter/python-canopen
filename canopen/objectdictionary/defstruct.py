from .datatypes import UNSIGNED8, UNSIGNED16
from .deftype import DefType
from .domain import Domain
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
		if not isinstance(value, Variable) or isinstance(value, (DefType, Domain)):
			raise TypeError()
		if value.data_type != UNSIGNED8 and value.data_type != UNSIGNED16:
			raise ValueError()
		if value.subindex == 0 and value.data_type != UNSIGNED8:
			raise ValueError()
		if value.access_type != "ro" and value.access_type != "const":
			raise ValueError()
		
		Array.add(self, value)
