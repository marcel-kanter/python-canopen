import canopen.objectdictionary
from .node import Node
from .service import NMTSlave, EMCYProducer, SDOServer, PDOConsumer, PDOProducer


class LocalNode(Node):
	""" Representation of a local CANopen node.
	
	This class represents a local CANopen node and can be accessed by other nodes on the bus. It is an auto-associative mapping and may contain zero or more variables, records or arrays.
	"""
	def __init__(self, name, node_id, dictionary):
		""" Initializes a LocalNode.
		
		:param name: Name of the node
		
		:param node_id: Identifier of the node. Must be 1 ... 127 or 255
		
		:param dictionary: Object dictionary to use with this node
		
		:raises: TypeError, ValueError
		"""
		Node.__init__(self, name, node_id, dictionary)
		self._data = {}
		self.nmt = NMTSlave(self)
		self.emcy = EMCYProducer(self)
		self.sdo = SDOServer(self)
		self.rpdo = {1: PDOConsumer(self), 2: PDOConsumer(self), 3: PDOConsumer(self), 4: PDOConsumer(self)}
		self.tpdo = {1: PDOProducer(self), 2: PDOProducer(self), 3: PDOProducer(self), 4: PDOProducer(self)}
	
	def attach(self, network):
		""" Attach the node and then all services to the network. It does NOT add or assign the node to the network.
		If the node is already attached to a network, it is automatically detached.
		Raises RuntimeError if the node is already attached to the network.
		
		:param network: The network to attach the node to.
		
		:raises: RuntimeError, TypeError, ValueError
		"""
		Node.attach(self, network)
		self.nmt.attach()
		self.sdo.attach()
		self.emcy.attach()
		self.tpdo[1].attach(0x180 + self._id)
		self.tpdo[2].attach(0x280 + self._id)
		self.tpdo[3].attach(0x380 + self._id)
		self.tpdo[4].attach(0x480 + self._id)
		self.rpdo[1].attach(0x200 + self._id)
		self.rpdo[2].attach(0x300 + self._id)
		self.rpdo[3].attach(0x400 + self._id)
		self.rpdo[4].attach(0x500 + self._id)
	
	def detach(self):
		""" Detaches all services and then the node from the network. It does NOT remove or delete the node from the network.
		
		:raises: RuntimeError
		"""
		for i in self.rpdo:
			self.rpdo[i].detach()
		for i in self.tpdo:
			self.tpdo[i].detach()
		self.emcy.detach()
		self.sdo.detach()
		self.nmt.detach()
		Node.detach(self)
	
	def get_data(self, index, subindex):
		""" Gets data of an object of the node.
		The data is stored in the data dictionary in the local object.
		
		:param index: The index of the object
		
		:param subindex: The sub index of the object
		
		:raises: KeyError
		"""
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
		""" Sets data for an object of the node.
		The data is stored in the data dictionary in the local object.
		
		:param index: The index of the object
		
		:param subindex: The sub index of the object
		
		:param data: The data to set
		"""
		self._data[(index, subindex)] = data
