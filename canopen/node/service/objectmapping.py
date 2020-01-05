class ObjectMapping(object):
	def __init__(self):
		self._items = []
	
	def __getitem__(self, slot):
		""" Gets a variable from the mapping.
		Raises a KeyError if the slot is unused.
		
		:param slot: The slot from with the variable should be returned. Must be a non-negativer integer lower than the number of mapped variables.
		
		:returns: A tuple in the form of (entry, length) with entry beeing a Variable or a tuple in the form of (index, subindex)
		
		:raises: IndexError
		"""
		return self._items[slot]
	
	def __len__(self):
		""" Gets the number of mapped variables.
		
		:returns: number of mapped variables
		"""
		return len(self._items)
	
	def append(self, variable, length):
		""" Appends a variable to the mapping, only length bits should be used.
		
		:param variable: Variable to append. Must be a Variable from object dictionary, a Variable from node or a tuple in the form of (index, subindex).
		
		:param length: Number of bits to use. Must be a non-negative integer.
		
		:raises: TypeError, ValueError
		"""
		if int(length) < 0:
			raise ValueError()
		
		entry = variable
		
		self._items.append((entry, length))
