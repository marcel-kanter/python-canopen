import canopen.node


class Service(object):
	""" Service
	
	This class is the base class for all services of a node.
	"""
	def __init__(self):
		self._node = None
		self._callbacks = {}
	
	def attach(self, node):
		""" Attaches the ``Service`` to a ``Node``. It does NOT append or assign this ``Service`` to the ``Node``. """
		if not isinstance(node, canopen.node.Node):
			raise TypeError()
		if self._node == node:
			raise ValueError()
		if self._node != None:
			self.detach()
		
		self._node = node
	
	def detach(self):
		""" Detaches the ``Service`` from the ``Node``. It does NOT remove or delete the ``Service`` from the ``Node``. """
		if self._node == None:
			raise RuntimeError()
		
		self._node = None
	
	def add_callback(self, event, callback):
		""" Adds the given callback for the event. """
		if not callable(callback):
			raise TypeError()
		if not event in self._callbacks:
			raise ValueError()
		
		self._callbacks[event].append(callback)
	
	def remove_callback(self, event, callback):
		""" Removes the callback for the event. """
		if not callable(callback):
			raise TypeError()
		if not event in self._callbacks:
			raise ValueError()
		
		self._callbacks[event].remove(callback)
	
	def notify(self, event, *args):
		""" Call the callbacks for the given event. First argument for each callback is event.
		If a callback raises an exception, it will be dropped. """
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
