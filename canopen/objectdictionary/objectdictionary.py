import collections
from .array import Array
from .defstruct import DefStruct
from .deftype import DefType
from .domain import Domain
from .record import Record
from .variable import Variable


class ObjectDictionary(collections.abc.Collection):
	""" Representation of a CANopen object dictionary.
	
	This class is the representation of one CANopen object dictionary. It is a mutable auto-associative mapping and may contain zero or more elements of type Array, DefStruct, DefType, Record or Variable.
	"""
	def __init__(self):
		self._items_index = {}
		self._items_name = {}
	
	def __eq__(self, other):
		""" Indicates whether some other object is "equal to" this one. """
		if self is other:
			return True
		if self.__class__ != other.__class__:
			return False
		if self._items_index != other._items_index:
			return False
		return True
	
	def __contains__(self, key):
		""" Returns True if the object dictionary contains a variable, record or array with the specified index or name. """
		try:
			self[key]
		except:
			return False
		else:
			return True
	
	def __iter__(self):
		""" Returns an iterator over all indexes of the objects in the object dictionary. """
		return iter(self._items_index)
	
	def __len__(self):
		""" Returns the number of objects in the object dictionary. """
		return len(self._items_index)
	
	def __getitem__(self, key):
		""" Returns the variable, record or array identified by the name or the index. """
		if key in self._items_index:
			return self._items_index[key]
		if key in self._items_name:
			return self._items_name[key]
		raise KeyError()
	
	def __delitem__(self, key):
		""" Removes the variable, record or array identified by the name or the index from the object dictionary. """
		item = self[key]
		del self._items_index[item.index]
		del self._items_name[item.name]
	
	def add(self, value):
		""" Adds a variable, record or array to the object dictionary. It may be accessed later by the name or the index. """
		if not isinstance(value, (Array, DefStruct, DefType, Domain, Record, Variable)):
			raise TypeError()
		if value.index in self._items_index or value.name in self._items_name:
			raise ValueError()
		
		self._items_index[value.index] = value
		self._items_name[value.name] = value
