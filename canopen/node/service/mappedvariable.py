class MappedVariable(object):
	def __init__(self, mapping, slot, entry, size):
		self._mapping = mapping
		self._slot = slot
		self._entry = entry
		self._size = size
	
	@property
	def index(self):
		if isinstance(self._entry, tuple):
			return self._entry[0]
		else:
			return self._entry.index
		
	@property
	def subindex(self):
		if isinstance(self._entry, tuple):
			return self._entry[1]
		else:
			return self._entry.subindex
	
	@property
	def size(self):
		return self._size
