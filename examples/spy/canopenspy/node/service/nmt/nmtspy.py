from canopen.node.service import Service


class NMTSpy(Service):
	def __init__(self):
		Service.__init__(self)
	
	def attach(self, node):
		Service.attach(self, node)
		self._node.network.subscribe(self.on_node_control, 0x000)
		self._node.network.subscribe(self.on_error_control, 0x700 + self._node.id)
	
	def detach(self):
		self._node.network.unsubscribe(self.on_error_control, 0x700 + self._node.id)
		self._node.network.unsubscribe(self.on_node_control, 0x000)
		Service.detach(self)
	
	def on_node_control(self, message):
		print(message)
		print("NMT: node control")
	
	def on_error_control(self, message):
		print(message)
		print("NMT: error control")
