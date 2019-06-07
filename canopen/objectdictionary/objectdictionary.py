import collections
from .array import Array
from .record import Record
from .variable import Variable


class ObjectDictionary(collections.abc.Collection):
	""" Representation of a CANopen object dictionary.
	
	This class is the representation of one CANopen object dictionary. It is an auto-associative list and may contain zero or more CANopen variables, records or arrays.
	"""
	def __init__(self):
		self._items_index = {}
		self._items_name = {}
	
	def __contains__(self, key):
		""" Returns true if the object dictionary contains a variable, record or array with the specified index or name. """
		try:
			self[key]
		except:
			return False
		else:
			return True
	
	def __iter__(self):
		""" Returns an iterator over all indexes of the elements in the object dictionary. """
		return iter(self._items_index)
	
	def __len__(self):
		""" Returns the number of elements in the object dictionary. """
		return len(self._items_index)
	
	def __getitem__(self, key):
		""" Returns the variable, record or array identified by the name or the index. """
		if key in self._items_index:
			return self._items_index[key]
		if key in self._items_name:
			return self._items_name[key]
		raise KeyError()
	
	def __delitem__(self, key):
		""" Removes the variable, record or array identified by the name of the index from the object dictionary. """
		item = self[key]
		del self._items_index[item.index]
		del self._items_name[item.name]
	
	def append(self, value):
		""" Appends a variable, record or array to the object dictionary. It may be accessed later by the name or the index. """
		if not isinstance(value, (Array, Record, Variable)):
			raise TypeError()
		if value.index in self._items_index or value.name in self._items_name:
			raise ValueError()
		
		self._items_index[value.index] = value
		self._items_name[value.name] = value
