from .datatypes import DOMAIN
from .variable import Variable


class Domain(Variable):
	""" Representation of a Domain object of an object dictionary.
	
	This class is a representation of a Domain object of an object dictionary. Basically this is a Variable with fixed subindex and data_type.
	"""
	def __init__(self, name, index, access_type = "rw"):
		Variable.__init__(self, name, index, 0, DOMAIN, access_type)
