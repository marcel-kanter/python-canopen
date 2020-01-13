import collections
from .datatypes import UNSIGNED8, UNSIGNED32
from .variable import Variable


class Array(collections.abc.Collection):
	""" Representation of an array of a CANopen object dictionary.
	
	This class is the representation of an array of a CANopen object dictionary. It is a mutable auto-associative mapping and may contain zero or more variables.
	"""
	def __init__(self, name, index, data_type, description = ""):
		if index < 0 or index > 65535:
			raise ValueError()
		if int(data_type) < 0x0000 or int(data_type) > 0x1000:
			raise ValueError()
		
		self._name = str(name)
		self._index = int(index)
		self._description = str(description)
		
		self._object_type = 8
		self._data_type = int(data_type)
		
		self._items_subindex = {}
		self._items_name = {}
	
	def __eq__(self, other):
		""" Indicates whether some other object is "equal to" this one. """
		if type(self) != type(other):
			return False
		return self is other or (self._object_type == other._object_type and self._name == other._name and self._index == other._index and self._description == other._description and self._data_type == other._data_type and self._items_subindex == other._items_subindex)
	
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
		return iter(self._items_subindex.values())
	
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
		if not isinstance(value, Variable):
			raise TypeError()
		# Allow objects with object type 7 (Variable) only. DefType and Domain are sub-classes of Variable and thus will pass the isinstance check.
		if value.object_type != 7:
			raise TypeError()
		if value.subindex in self._items_subindex or value.name in self._items_name:
			raise ValueError()
		if value.index != self._index:
			raise ValueError()
		
		self._items_subindex[value.subindex] = value
		self._items_name[value.name] = value
	
	@property
	def object_type(self):
		""" Returns the object type as defined in DS301 v4.02 Table 42: Object code usage.
		"""
		return self._object_type
	
	@property
	def index(self):
		return self._index
	
	@property
	def name(self):
		return self._name
	
	@property
	def description(self):
		return self._description
	
	@description.setter
	def description(self, x):
		self._description = x
	
	@property
	def data_type(self):
		"""
		Returns the data type as defined in DS301 v4.02 Table 44: Object dictionary data types.
		"""
		return self._data_type
