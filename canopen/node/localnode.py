from .node import Node
from .service import NMTSlave, EMCYProducer


class LocalNode(Node):
	def __init__(self, name, node_id):
		Node.__init__(self, name, node_id)
		self.nmt = NMTSlave()
		self.emcy = EMCYProducer()
	
	def attach(self, network):
		Node.attach(self, network)
		self.nmt.attach(self)
		self.emcy.attach(self)
	
	def detach(self):
		self.emcy.detach()
		self.nmt.detach()
		Node.detach(self)
