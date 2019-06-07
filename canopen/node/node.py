import canopen


class Node(object):
	""" Representation of a CANopen node.
	
	This class is a basic representation of a CANopen node.
	"""
	def __init__(self, name, node_id, dictionary):
		if node_id < 1 or node_id > 127:
			raise ValueError()
		if not isinstance(dictionary, canopen.ObjectDictionary):
			raise TypeError()
		
		self._dictionary = dictionary
		self._id = node_id
		self._name = name
		self._network = None
	
	def attach(self, network):
		""" Attach this node to a network. It does NOT append or assign the node to the network. """
		if not isinstance(network, canopen.Network):
			raise TypeError()
		if self._network == network:
			raise ValueError()
		if self._network != None:
			self.detach()
		
		self._network = network
	
	def detach(self):
		""" Detach this node from the network. It does NOT remove or delete the node from the network. """
		if self._network == None:
			raise RuntimeError()
		
		self._network = None
	
	@property
	def dictionary(self):
		return self._dictionary
	
	@property
	def id(self):
		return self._id
	
	@property
	def name(self):
		return self._name
	
	@property
	def network(self):
		return self._network
