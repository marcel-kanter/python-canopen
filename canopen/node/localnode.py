import canopen.objectdictionary
from .node import Node
from .service import NMTSlave, EMCYProducer, SDOServer


class LocalNode(Node):
	""" Representation of a local CANopen node.
	
	This class represents a local CANopen node and can be accessed by other nodes on the bus. It is an auto-associative list and may contain zero or more variables, records or arrays.
	"""
	def __init__(self, name, node_id, dictionary):
		Node.__init__(self, name, node_id, dictionary)
		self._data = {}
		self.nmt = NMTSlave()
		self.emcy = EMCYProducer()
		self.sdo = SDOServer()
	
	def attach(self, network):
		""" Attach the node and then all services to the network. It does NOT append or assign the node to the network."""
		Node.attach(self, network)
		self.nmt.attach(self)
		self.sdo.attach(self)
		self.emcy.attach(self)
	
	def detach(self):
		""" Detaches all services and then the node from the network. It does NOT remove or delete the node from the network."""
		self.emcy.detach()
		self.sdo.detach()
		self.nmt.detach()
		Node.detach(self)
	
	def get_data(self, index, subindex):
		if not (index, subindex) in self._data:
			try:
				item = self._dictionary[index]
			except:
				raise KeyError()
				
			if not isinstance(item, canopen.objectdictionary.Variable):
				try:
					item = item[subindex]
				except:
					raise KeyError()
			
			return item.default
		else:
			return self._data[(index, subindex)]
	
	def set_data(self, index, subindex, data):
		self._data[(index, subindex)] = data
