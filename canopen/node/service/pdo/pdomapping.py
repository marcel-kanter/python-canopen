from canopen.node.service.objectmapping import ObjectMapping


class PDOMapping(ObjectMapping):
	"""
	Class for handling the mapping of Variables to data byte arrays for the use with PDOs. 
	"""
	def __init__(self):
		ObjectMapping.__init__(self)
