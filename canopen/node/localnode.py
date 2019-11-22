import canopen.objectdictionary
from .node import Node
from .service import NMTSlave, EMCYProducer, SDOServer, LocalPDOConsumer, LocalPDOProducer


class LocalNode(Node):
	""" Representation of a local CANopen node.
	
	This class represents a local CANopen node and can be accessed by other nodes on the bus. It is an auto-associative mapping and may contain zero or more variables, records or arrays.
	"""
	def __init__(self, name, node_id, dictionary):
		Node.__init__(self, name, node_id, dictionary)
		self._data = {}
		self.nmt = NMTSlave()
		self.emcy = EMCYProducer()
		self.sdo = SDOServer()
		self.rpdo = {1: LocalPDOConsumer(), 2: LocalPDOConsumer(), 3: LocalPDOConsumer(), 4: LocalPDOConsumer()}
		self.tpdo = {1: LocalPDOProducer(), 2: LocalPDOProducer(), 3: LocalPDOProducer(), 4: LocalPDOProducer()}
	
	def attach(self, network):
		""" Attach the node and then all services to the network. It does NOT add or assign the node to the network."""
		Node.attach(self, network)
		self.nmt.attach(self)
		self.sdo.attach(self)
		self.emcy.attach(self)
		self.tpdo[1].attach(self, 0x180 + self._id)
		self.tpdo[2].attach(self, 0x280 + self._id)
		self.tpdo[3].attach(self, 0x380 + self._id)
		self.tpdo[4].attach(self, 0x480 + self._id)
		self.rpdo[1].attach(self, 0x200 + self._id)
		self.rpdo[2].attach(self, 0x300 + self._id)
		self.rpdo[3].attach(self, 0x400 + self._id)
		self.rpdo[4].attach(self, 0x500 + self._id)
	
	def detach(self):
		""" Detaches all services and then the node from the network. It does NOT remove or delete the node from the network."""
		for i in self.rpdo:
			self.rpdo[i].detach()
		for i in self.tpdo:
			self.tpdo[i].detach()
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
			
			return item.default_value
		else:
			return self._data[(index, subindex)]
	
	def set_data(self, index, subindex, data):
		self._data[(index, subindex)] = data
