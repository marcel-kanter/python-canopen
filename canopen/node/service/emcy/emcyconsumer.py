import struct
from canopen.node.service import Service


class EMCYConsumer(Service):
	""" EMCY consumer
	
	This class is an implementation of a DS301 EMCY consumer. 
	"""
	def __init__(self):
		Service.__init__(self)
		self._callbacks = {"emcy": []}
	
	def attach(self, node):
		""" Attaches the service to a node. It does NOT append or assign this service to the node. """
		Service.attach(self, node)
		self._node.network.subscribe(self.on_emcy, 0x80 + self._node.id)
	
	def detach(self):
		""" Detaches the service from the node. It does NOT remove or delete the service from the node. """
		if self._node == None:
			raise RuntimeError()
		
		self._node.network.unsubscribe(self.on_emcy, 0x80 + self._node.id)
		Service.detach(self)
	
	def add_callback(self, callback, event):
		""" Adds the given callback to the event. """
		if not callable(callback):
			raise TypeError()
		if not event in self._callbacks:
			raise ValueError()
		
		self._callbacks[event].append(callback)
	
	def remove_callback(self, callback, event):
		""" Removes the callback from the event. """
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
				callback(event, self._node, *args)
			except:
				pass
	
	def on_emcy(self, message):
		error_code, error_register, data = struct.unpack("<HB5s", message.data)
		
		self.notify("emcy", error_code, error_register, data)
