import collections
from .deftype import DefType
from .domain import Domain
from .variable import Variable


class Array(collections.abc.Collection):
	""" Representation of an array of a CANopen object dictionary.
	
	This class is the representation of an array of a CANopen object dictionary. It is a mutable auto-associative mapping and may contain zero or more variables.
	"""
	def __init__(self, name, index):
		if index < 0 or index > 65535:
			raise ValueError()
		
		self._object_type = 8
		self._name = name
		self._index = index
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
		""" Returns True if the array contains a variable with the specified subindex or name. """
		try:
			self[key]
		except:
			return False
		else:
			return True
	
	def __iter__(self):
		""" Returns an iterator over all subindexes of the variables in the array. """
		return iter(self._items_subindex)
	
	def __len__(self):
		""" Returns the number of variables in the array. """
		return len(self._items_subindex)
	
	def __getitem__(self, key):
		""" Returns the variable identified by the name or the subindex. """
		if key in self._items_subindex:
			return self._items_subindex[key]
		if key in self._items_name:
			return self._items_name[key]
		raise KeyError()
	
	def __delitem__(self, key):
		""" Removes the variable identified by the name of the subindex from the array. """
		item = self[key]
		del self._items_subindex[item.subindex]
		del self._items_name[item.name]
	
	def add(self, value):
		""" Adds a variable to the array. It may be accessed later by the name or the subindex. """
		if not isinstance(value, Variable) or isinstance(value, (DefType, Domain)):
			raise TypeError()
		if value.subindex in self._items_subindex or value.name in self._items_name:
			raise ValueError()
		if value.index != self._index:
			raise ValueError()
		
		self._items_subindex[value.subindex] = value
		self._items_name[value.name] = value
	
	@property
	def object_type(self):
		"""
		Returns the object type as defined in DS301 v4.02 Table 42: Object code usage.
		"""
		return self._object_type
	
	@property
	def index(self):
		return self._index
	
	@property
	def name(self):
		return self._name
