import canopen.objectdictionary


class Variable(object):
	def __init__(self, node, entry):
		if not isinstance(node, canopen.Node):
			raise TypeError()
		if not isinstance(entry, canopen.objectdictionary.Variable):
			raise TypeError()
		self._node = node
		self._entry = entry
