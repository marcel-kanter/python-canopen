from .node import Node
from .service import NMTMaster, EMCYConsumer, SDOClient


class RemoteNode(Node):
	""" Representation of a remote CANopen node.
	
	This class represents a remote CANopen node and can be used to access other nodes on the bus. It is an auto-associative list and may contain zero or more variables, records or arrays.
	"""
	def __init__(self, name, node_id, dictionary):
		Node.__init__(self, name, node_id, dictionary)
		self.nmt = NMTMaster()
		self.emcy = EMCYConsumer()
		self.sdo = SDOClient()
	
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
		return self.sdo.upload(index, subindex)
	
	def set_data(self, index, subindex, value):
		self.sdo.download(index, subindex, value)
