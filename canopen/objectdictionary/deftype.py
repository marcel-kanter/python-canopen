from .datatypes import UNSIGNED32
from .variable import Variable


class DefType(Variable):
	""" Representation of a DefType of an object dictionary.
	
	This class is a representation of a DefType of an object dictionary. Basically this is a Variable with fixed subindex, data_type and access_type.
	Upon read, it should return the number of bits needed to encode the type.
	"""
	def __init__(self, name, index):
		Variable.__init__(self, name, index, 0, UNSIGNED32, "ro")
		self._object_type = 5
	
	@property
	def access_type(self):
		return self._access_type
	
	@access_type.setter
	def access_type(self, x):
		raise AttributeError()
