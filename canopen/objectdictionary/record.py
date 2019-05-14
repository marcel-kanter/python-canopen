import collections
from .variable import Variable


class Record(collections.abc.Collection):
	def __init__(self, name, index):
		if index < 0 or index > 65535:
			raise ValueError()
		
		self._name = name
		self._index = index
		self._items_subindex = {}
		self._items_name = {}
	
	def __contains__(self, key):
		try:
			x = self[key]
		except:
			return False
		else:
			return True
	
	def __iter__(self):
		return iter(self._items_subindex)
	
	def __len__(self):
		return len(self._items_subindex)
	
	def __getitem__(self, key):
		if key in self._items_subindex:
			return self._items_subindex[key]
		if key in self._items_name:
			return self._items_name[key]
		raise KeyError()
	
	def __delitem__(self, key):
		item = self[key]
		del self._items_subindex[item.subindex]
		del self._items_name[item.name]
	
	def append(self, value):
		if not isinstance(value, Variable):
			raise TypeError()
		if value.subindex in self._items_subindex or value.name in self._items_name:
			raise ValueError()
		if value.index != self._index:
			raise ValueError()
		
		self._items_subindex[value.subindex] = value
		self._items_name[value.name] = value
	
	@property
	def index(self):
		return self._index
	
	@property
	def name(self):
		return self._name
