import canopen
from .service import NMTSpy


class SpyNode(canopen.Node):
	def __init__(self, name, node_id):
		canopen.Node.__init__(self, name, node_id, canopen.ObjectDictionary())
		self.nmt = NMTSpy()
	
	def attach(self, network):
		canopen.Node.attach(self, network)
		self.nmt.attach(self)
	
	def detach(self):
		self.nmt.detach()
		canopen.Node.detach(self)
