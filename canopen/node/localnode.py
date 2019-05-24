from .node import Node
from .service import NMTSlave


class LocalNode(Node):
	def __init__(self, name, node_id):
		super(LocalNode, self).__init__(name, node_id)
		self.nmt = NMTSlave()
	
	def attach(self, network):
		super(LocalNode, self).attach(network)
		self.nmt.attach(self)
	
	def detach(self):
		self.nmt.detach()
		super(LocalNode, self).detach()
