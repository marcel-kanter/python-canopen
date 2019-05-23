import collections
from .array import Array
from .record import Record
from .variable import Variable


class ObjectDictionary(collections.abc.Collection):
	def __init__(self):
		self._items_index = {}
		self._items_name = {}
	
	def __contains__(self, key):
		try:
			self[key]
		except:
			return False
		else:
			return True
	
	def __iter__(self):
		return iter(self._items_index)
	
	def __len__(self):
		return len(self._items_index)
	
	def __getitem__(self, key):
		if key in self._items_index:
			return self._items_index[key]
		if key in self._items_name:
			return self._items_name[key]
		raise KeyError()
	
	def __delitem__(self, key):
		item = self[key]
		del self._items_index[item.index]
		del self._items_name[item.name]
	
	def append(self, value):
		if not isinstance(value, (Array, Record, Variable)):
			raise TypeError()
		if value.index in self._items_index or value.name in self._items_name:
			raise ValueError()
		
		self._items_index[value.index] = value
		self._items_name[value.name] = value
