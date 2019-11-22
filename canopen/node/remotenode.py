from .node import Node
from .service import NMTMaster, EMCYConsumer, SDOClient, RemotePDOConsumer, RemotePDOProducer


class RemoteNode(Node):
	""" Representation of a remote CANopen node.
	
	This class represents a remote CANopen node and can be used to access other nodes on the bus. It is an auto-associative mapping and may contain zero or more variables, records or arrays.
	"""
	def __init__(self, name, node_id, dictionary):
		Node.__init__(self, name, node_id, dictionary)
		self.nmt = NMTMaster()
		self.emcy = EMCYConsumer()
		self.sdo = SDOClient()
		self.rpdo = {1: RemotePDOConsumer(), 2: RemotePDOConsumer(), 3: RemotePDOConsumer(), 4: RemotePDOConsumer()}
		self.tpdo = {1: RemotePDOProducer(), 2: RemotePDOProducer(), 3: RemotePDOProducer(), 4: RemotePDOProducer()}
	
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
		return self.sdo.upload(index, subindex)
	
	def set_data(self, index, subindex, value):
		self.sdo.download(index, subindex, value)
