from canopen.node.service import Service


class NMTMaster(Service):
	""" NMTMaster service.
	
	This class is an implementation of the NMT master. The nmt state of the node can be accessed by the state property.
	"""
	def __init__(self):
		Service.__init__(self)
		self._state = 0

	def attach(self, node):
		""" Attaches the service to a node. It does NOT append or assign this service to the node. """
		Service.attach(self, node)
		self._state = 0
		self._node.network.subscribe(self.on_error_control, 0x700 + self._node.id)
	
	def detach(self):
		""" Detaches the service from the node. It does NOT remove or delete the service from the node. """
		if self._node == None:
			raise RuntimeError()
		
		self._node.network.unsubscribe(self.on_error_control, 0x700 + self._node.id)
		Service.detach(self)
	
	def on_error_control(self, message):
		""" Handler for error control requests. It catches all status messages from the remote node and updates the state property. """
		if message.is_remote_frame:
			return
		if message.dlc != 1:
			return
		
		self._state = message.data[0] & 0x7F
	
	@property
	def state(self):
		return self._state
