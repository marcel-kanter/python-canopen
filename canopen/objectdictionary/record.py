import collections
from .objectdictionaryelement import ObjectDictionaryElement
from .deftype import DefType
from .domain import Domain
from .variable import Variable


class Record(collections.abc.Collection, ObjectDictionaryElement):
	""" Representation of a record of a CANopen object dictionary.
	
	This class is the representation of a record of a CANopen object dictionary. It is a mutable auto-associative mapping and may contain zero or more variables.
	"""
	def __init__(self, name, index):
		ObjectDictionaryElement.__init__(self, name, index)
		
		self._object_type = 9
		self._items_subindex = {}
		self._items_name = {}
	
	def __eq__(self, other):
		""" Indicates whether some other object is "equal to" this one. """
		if self is other:
			return True
		if self.__class__ != other.__class__:
			return False
		if self._name != other._name or self._index != other.index:
			return False
		if self._items_subindex != other._items_subindex:
			return False
		return True
	
	def __contains__(self, key):
		""" Returns True if the record contains a variable with the specified subindex or name. """
		try:
			self[key]
		except:
			return False
		else:
			return True
	
	def __iter__(self):
		""" Returns an iterator over all subindexes of the variables in the record. """
		return iter(self._items_subindex.values())
	
	def __len__(self):
		""" Returns the number of variables in the record. """
		return len(self._items_subindex)
	
	def __getitem__(self, key):
		""" Returns the variable identified by the name or the subindex. """
		if key in self._items_subindex:
			return self._items_subindex[key]
		if key in self._items_name:
			return self._items_name[key]
		raise KeyError()
	
	def __delitem__(self, key):
		""" Removes the variable identified by the name of the subindex from the record. """
		item = self[key]
		del self._items_subindex[item.subindex]
		del self._items_name[item.name]
	
	def add(self, value):
		""" Adds a variable to the record. It may be accessed later by the name or the subindex. """
		if not isinstance(value, Variable) or isinstance(value, (DefType, Domain)):
			raise TypeError()
		if value.subindex in self._items_subindex or value.name in self._items_name:
			raise ValueError()
		if value.index != self._index:
			raise ValueError()
		
		self._items_subindex[value.subindex] = value
		self._items_name[value.name] = value
