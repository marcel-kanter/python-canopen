import canopen
import time
from .service import NMTSpy, SYNCSpy, TIMESpy


class SpyNode(canopen.Node):
	def __init__(self, name, node_id):
		canopen.Node.__init__(self, name, node_id, canopen.ObjectDictionary())
		self.nmt = NMTSpy()
		self.sync = SYNCSpy()
		self.time = TIMESpy()
		self.sync.add_callback("sync", self.sync_callback)
		self.time.add_callback("time", self.time_callback)
	
	def attach(self, network):
		canopen.Node.attach(self, network)
		self.nmt.attach(self)
		self.sync.attach(self)
		self.time.attach(self)
	
	def detach(self):
		self.time.detach()
		self.sync.detach()
		self.nmt.detach()
		canopen.Node.detach(self)
	
	def sync_callback(self, event, node, counter):
		if counter == None:
			print("SYNC: no counter")
		else:
			print("SYNC: counter=" + str(counter))
	
	def time_callback(self, event, node, t):
		print("TIME: time=" + time.ctime(t))
