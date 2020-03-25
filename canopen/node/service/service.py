from canopen.node import Node


class Service(object):
	""" Service
	
	This class is the base class for all services of a node.
	"""
	def __init__(self, node):
		""" Initializes the service
		
		:param node: The node, to which this service belongs to.
			Must be of type canopen.node.Node
		
		:raises: TypeError
		"""
		if not isinstance(node, Node):
			raise TypeError()
		
		self._node = node
		self._callbacks = {}
		self._enabled = True
	
	def attach(self):
		""" Attach handler. Must be called when the node gets attached to the network.
		This is a stub for subclasses, always raises NotImplementedError.
		
		:raises: NotImplementedError
		"""
		raise NotImplementedError
	
	def detach(self):
		""" Detach handler. Must be called when the node gets detached from the network.
		This is a stub for subclasses, always raises NotImplementedError.
		
		:raises: NotImplementedError
		"""
		raise NotImplementedError
	
	def is_attached(self):
		""" Returns True if the service is attached.
		This is a stub for subclasses, always raises NotImplementedError.
		
		:raises: NotImplementedError
		"""
		raise NotImplementedError
	
	def enable(self):
		""" Enables this service
		"""
		self._enabled = True
	
	def disable(self):
		""" Disables this service
		"""
		self._enabled = False
	
	def is_enabled(self):
		"""
		:returns: A boolean. True, if this service is enabled.
		"""
		return self._enabled
	
	def add_callback(self, event, callback):
		""" Adds the given callback for the event.
		Raises TypeError if the callback is not callable.
		Raises KeyError if the event is not supported/found.
		
		:param event: The name of the event
		
		:param callback: The callback function.
			Must be callable
		
		:raises: TypeError, KeyError
		"""
		if not callable(callback):
			raise TypeError()
		
		self._callbacks[event].append(callback)
	
	def add_event(self, event):
		""" Adds an event to this service.
		Raises KeyError if the event is already in the list.
		
		:param event: The name of the event.
		
		:raises: ValueError
		"""
		if event in self._callbacks:
			raise KeyError()
		
		self._callbacks[event] = []
	
	def remove_callback(self, event, callback):
		""" Removes the callback for the event.
		Raises KeyError if the event is not supported/found.
		Raises ValueError if the callback was not found.
		
		:param event: The name of the event
		
		:param callback: The callback function.
			Must be callable
		
		:raises: KeyError, ValueError
		"""
		self._callbacks[event].remove(callback)
	
	def remove_event(self, event):
		""" Removes an event from the service.
		Raises KeyError if the event is not found.
		
		:param event: The name of the event.
		
		:raises: KeyError
		"""
		del self._callbacks[event]
	
	def notify(self, event, *args):
		""" Call the callbacks for the given event. First argument for each callback is event.
		If a callback raises an exception, it will be dropped.
		Raises KeyError if the event is not found.
		
		:param event: The name of the event
		
		:param args: A list of arguments to pass additionally to the callback
		
		:raises: KeyError
		"""		
		for callback in self._callbacks[event]:
			try:
				callback(event, *args)
			except:
				pass
	
	@property
	def node(self):
		""" Returns the node this service belongs to.
		"""
		return self._node
