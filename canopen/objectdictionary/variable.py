import collections


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
