class Node(object):
	def __init__(self, name, id):
		if id < 1 or id > 127:
			raise ValueError()
		
		self._id = id
		self._name = name
	
	@property
	def id(self):
		return self._id
	
	@property
	def name(self):
		return self._name
