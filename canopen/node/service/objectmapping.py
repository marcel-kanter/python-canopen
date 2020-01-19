from canopen.node.service.service import Service
from canopen.node.service.mappedvariable import MappedVariable


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
		
		:returns: A tuple in the form of (entry, length) with entry beeing a MappedVariable
		
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
		length = int(length)
		if length < 0:
			raise ValueError()
		
		entry = MappedVariable(self, len(self._items), variable)
		
		self._items.append((entry, length))
		self._size += length
	
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
