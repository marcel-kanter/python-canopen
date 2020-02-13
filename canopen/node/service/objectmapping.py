from canopen.node.service.service import Service
from canopen.node.service.mappedvariable import MappedVariable
from canopen.objectdictionary import Variable


class ObjectMapping(object):
	def __init__(self, service):
		"""
		:param service: The service to which this mapping belongs to. Must be of type canpen.node.service.Service
		
		:raises: TypeError
		"""
		if not isinstance(service, Service):
			raise TypeError()
		
		self._service = service
		self._items = []
		self._size = 0
	
	def __getitem__(self, slot):
		""" Gets a variable from the mapping.
		Raises a KeyError if the slot is unused.
		
		:param slot: The slot from with the variable should be returned. Must be a non-negativer integer lower than the number of mapped variables.
		
		:returns: The MappedVariable in the slot
		
		:raises: IndexError
		"""
		entry, size = self._items[slot]
		
		return MappedVariable(self, slot, entry, size)
	
	def __len__(self):
		""" Gets the number of mapped variables.
		
		:returns: number of mapped variables
		"""
		return len(self._items)
	
	def append(self, variable, size):
		""" Appends a variable to the mapping, only size bits should be used.
		
		:param variable: Variable to append. Must be a Variable from object dictionary, a Variable from node or a tuple in the form of (index, subindex).
		
		:param size: Number of bits to use. Must be a non-negative integer.
		
		:raises: TypeError, ValueError
		"""
		size = int(size)
		if size < 0:
			raise ValueError()
		
		if isinstance(variable, tuple):
			index = variable[0]
			subindex = variable[1]
		else:
			index = variable.index
			subindex = variable.subindex
		
		# If the index does not belong to a dummy value (index < 0x20), use the variable of the dictionary
		if index >= 0x20:
			try:
				variable = self._service.node.dictionary[index]
			except:
				raise ValueError()
			
			if not isinstance(variable, Variable):
				try:
					variable = variable[subindex]
				except:
					raise ValueError()
		
		self._items.append((variable, size))
		self._size += size
	
	def clear(self):
		""" Removes all mapped variables.
		"""
		self._items.clear()
		self._size = 0
	
	@property
	def size(self):
		""" Returns the overall number of bits of the mapped variables.
		"""
		return self._size
