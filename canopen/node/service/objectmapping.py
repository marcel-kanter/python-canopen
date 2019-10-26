class ObjectMapping(object):
	"""
	Base class for mappings of Variables to data byte arrays.
	"""
	def __init__(self):
		self._elements = []
	
	def __eq__(self, other):
		""" Indicates whether some other object is "equal to" this one. """
		if self is other:
			return True
		if self.__class__ != other.__class__:
			return False
		if self._elements != other._elements:
			return False
		return True
	
	def __contains__(self, x):
		return x in self._elements
	
	def __iter__(self):
		return iter(self._elements)
	
	def __len__(self):
		return len(self._elements)
		
	def append(self, x):
		self._elements.append(x)
	
	def clear(self):
		self._elements.clear()
	
	def insert(self, index, x):
		self._elements.insert(index, x)
	
	def remove(self, x):
		self._elements.remove(x)
