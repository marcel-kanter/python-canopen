class Node(object):
	def __init__(self, id):
		if id < 1 or id > 127:
			raise ValueError()
		
		self._id = id
	
	@property
	def id(self):
		return self._id
