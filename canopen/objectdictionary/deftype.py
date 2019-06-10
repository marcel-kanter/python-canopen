from .datatypes import UNSIGNED32
from .variable import Variable


class DefType(Variable):
	""" Representation of a DefType of an object dictionary.
	
	This class is a representation of a DefType of an object dictionary. Basically this is a Variable with fixed subindex, data_type and access_type.
	Upon read, it should return the number of bits needed to encode the type.
	"""
	def __init__(self, name, index):
		Variable.__init__(self, name, index, 0, UNSIGNED32, "ro")
