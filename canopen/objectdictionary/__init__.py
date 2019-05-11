import collections


class ObjectDictionary(collections.abc.Collection):
	def __init__(self):
		self._items_index = {}
		self._items_name = {}
	
	def __contains__(self, key):
		try:
			x = self[key]
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


class Array(collections.abc.Collection):
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


class Variable(object):
	def __init__(self, name, index, subindex):
		if index < 0 or index > 65535:
			raise ValueError()
		if subindex < 0 or subindex > 255:
			raise ValueError()
		
		self._name = name
		self._index = index
		self._subindex = subindex
	
	@property
	def index(self):
		return self._index
	
	@property
	def name(self):
		return self._name
	
	@property
	def subindex(self):
		return self._subindex
