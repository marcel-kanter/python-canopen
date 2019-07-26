import collections
import canopen.objectdictionary
from .array import Array
from .record import Record
from .variable import Variable
from .defstruct import DefStruct
from .deftype import DefType
from .domain import Domain


class Node(collections.abc.Collection):
	""" Representation of a CANopen node.
	
	This class is a basic representation of a CANopen node. It is an auto-associative list and may contain zero or more variables, records or arrays.
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
	
	def __contains__(self, key):
		""" Returns True if the node contains a variable, record or array with the specified index or name. """
		return key in self._dictionary
	
	def __iter__(self):
		""" Returns an iterator over all indexes of the objects in the node. """
		return iter(self._dictionary)
	
	def __len__(self):
		""" Returns the number of objects in the object dictionary. """
		return len(self._dictionary)
	
	def __getitem__(self, key):
		""" Returns the variable, record or array identified by the name or the index. """
		item = self._dictionary[key]
		if isinstance(item, canopen.objectdictionary.DefType):
			return DefType(self, item)
		if isinstance(item, canopen.objectdictionary.DefStruct):
			return DefStruct(self, item)
		if isinstance(item, canopen.objectdictionary.Domain):
			return Domain(self, item)
		if isinstance(item, canopen.objectdictionary.Variable):
			return Variable(self, item)
		if isinstance(item, canopen.objectdictionary.Array):
			return Array(self, item)
		if isinstance(item, canopen.objectdictionary.Record):
			return Record(self, item)
		raise NotImplementedError()
	
	def attach(self, network):
		""" Attach this node to a network. It does NOT append or assign the node to the network.
		If the node is already attached to a network, it is automatically detached. """
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
	
	def get_data(self, index, subindex):
		raise NotImplementedError()
	
	def set_data(self, index, subindex, data):
		raise NotImplementedError()
	
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
