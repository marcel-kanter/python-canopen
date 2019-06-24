import canopen.node


class Service(object):
	""" Service
	
	This class is the base class for all services of a node.
	"""
	def __init__(self):
		self._node = None
		self._callbacks = {}
	
	def attach(self, node):
		""" Attaches the service to a node. It does NOT append or assign this service to the node. """
		if not isinstance(node, canopen.node.Node):
			raise TypeError()
		if self._node == node:
			raise ValueError()
		if self._node != None:
			self.detach()
		
		self._node = node
	
	def detach(self):
		""" Detaches the service from the node. It does NOT remove or delete the service from the node. """
		if self._node == None:
			raise RuntimeError()
		
		self._node = None
	
	def add_callback(self, callback, event):
		""" Adds the given callback for the event. """
		if not callable(callback):
			raise TypeError()
		if not event in self._callbacks:
			raise ValueError()
		
		self._callbacks[event].append(callback)
	
	def remove_callback(self, callback, event):
		""" Removes the callback for the event. """
		if not callable(callback):
			raise TypeError()
		if not event in self._callbacks:
			raise ValueError()
		
		self._callbacks[event].remove(callback)
	
	def notify(self, event, *args):
		""" Call the callbacks for the given event. """
		if not event in self._callbacks:
			raise ValueError()
		
		for callback in self._callbacks[event]:
			try:
				callback(event, *args)
			except:
				pass
	
	@property
	def node(self):
		return self._node
