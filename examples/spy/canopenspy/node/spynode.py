import canopen
from .service import NMTSpy, SYNCSpy


class SpyNode(canopen.Node):
	def __init__(self, name, node_id):
		canopen.Node.__init__(self, name, node_id, canopen.ObjectDictionary())
		self.nmt = NMTSpy()
		self.sync = SYNCSpy()
		self.sync.add_callback(self.sync_callback, "sync")
	
	def attach(self, network):
		canopen.Node.attach(self, network)
		self.nmt.attach(self)
		self.sync.attach(self)
	
	def detach(self):
		self.sync.detach()
		self.nmt.detach()
		canopen.Node.detach(self)
	
	def sync_callback(self, event, node, counter):
		if counter == None:
			print("SYNC: no counter")
		else:
			print("SYNC: counter=" + str(counter))
