class ObjectDictionaryElement(object):
	def __init__(self, name, index):
		if index < 0 or index > 65535:
			raise ValueError()
		
		self._object_type = 0
		self._name = str(name)
		self._index = int(index)
		self._description = ""
	
	def __eq__(self, other):
		""" Indicates whether some other object is "equal to" this one. """
		if self is other:
			return True
		if self.__class__ != other.__class__:
			return False
		if self._object_type != other.object_type or self._name != other.name or self._index != other.index or self._description != other.description:
			return False
		return True
	
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
