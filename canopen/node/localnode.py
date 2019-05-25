from .node import Node
from .service import NMTSlave


class LocalNode(Node):
	def __init__(self, name, node_id):
		Node.__init__(self, name, node_id)
		self.nmt = NMTSlave()
	
	def attach(self, network):
		Node.attach(self, network)
		self.nmt.attach(self)
	
	def detach(self):
		self.nmt.detach()
		Node.detach(self)
