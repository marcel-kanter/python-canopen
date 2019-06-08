import collections.abc
import canopen.objectdictionary
from .variable import Variable


class Array(collections.abc.Collection):
	def __init__(self, node, entry):
		if not isinstance(node, canopen.Node):
			raise TypeError()
		if not isinstance(entry, canopen.objectdictionary.Array):
			raise TypeError()
		self._node = node
		self._entry = entry
	
	def __contains__(self, key):
		""" Returns True if the array contains a variable with the specified subindex or name. """
		return key in self._entry
	
	def __iter__(self):
		""" Returns an iterator over all indexes of the variables in the array. """
		return iter(self._entry)
	
	def __len__(self):
		""" Returns the number of variables in the array. """
		return len(self._entry)
	
	def __getitem__(self, key):
		""" Returns the variable identified by the name or the subindex. """
		item = self._entry[key]
		return Variable(self._node, item)
	
	@property
	def index(self):
		return self._entry._index
	
	@property
	def name(self):
		return self._entry._name
