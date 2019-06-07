import collections
import can
import canopen.node


class Network(collections.abc.Collection):
	""" Representation of a CANopen network.
	
	This class is the representation of one CANopen network. It is an auto-associative list and may contain zero or more CANopen nodes.

	To use Network together with a CAN bus, first the CAN bus instance must be created and then the network attached to the bus.
	In the end, the network may be detached from the CAN bus.
	"""
	def __init__(self):
		self._bus = None
		self._listeners = [MessageListener(self)]
		self._notifier = None
		self._subscribers = {}
		
		self._items_id = {}
		self._items_name = {}
	
	def __contains__(self, key):
		""" Returns true if the network contains a node with the specified name or id. """
		try:
			self[key]
		except:
			return False
		else:
			return True
	
	def __iter__(self):
		""" Returns an iterator over all ids of the nodes in the network. """
		return iter(self._items_id)
	
	def __len__(self):
		""" Returns the number of nodes in the network. """
		return len(self._items_id)
	
	def __getitem__(self, key):
		""" Returns the node identified by the name or the id. """
		if key in self._items_id:
			return self._items_id[key]
		if key in self._items_name:
			return self._items_name[key]
		raise KeyError()
	
	def __delitem__(self, key):
		""" Removes a node identified by the name of the id from the network. """
		item = self[key]
		item.detach()
		del self._items_id[item.id]
		del self._items_name[item.name]
	
	def append(self, value):
		""" Appends a node to the network. It may be accessed later by the name or the id. """
		if not isinstance(value, canopen.Node):
			raise TypeError()
		if value.id in self._items_id or value.name in self._items_name:
			raise ValueError()
		
		self._items_id[value.id] = value
		self._items_name[value.name] = value
		value.attach(self)
	
	def attach(self, bus):
		""" Attach the network to a CAN bus. """
		if not isinstance(bus, can.BusABC):
			raise TypeError()
		if self._bus == bus:
			raise ValueError()
		if self._bus != None:
			self.detach()
		
		self._bus = bus
		self._notifier = can.Notifier(self._bus, self._listeners)
	
	def detach(self):
		""" Detach the network from a CAN bus. """
		if self._bus == None:
			raise RuntimeError()
		
		self._notifier.stop()
		self._notifier = None
		self._bus = None
	
	def send(self, message):
		""" Sends a CAN message on the CAN bus. """
		if self._bus == None:
			raise RuntimeError()
		
		self._bus.send(message)
	
	def subscribe(self, callback, message_id):
		""" Adds a callback for messages with a specific message id to the network. """
		if not callable(callback):
			raise TypeError()
		
		if message_id not in self._subscribers:
			self._subscribers[message_id] = []
		self._subscribers[message_id].append(callback)
	
	def unsubscribe(self, callback, message_id):
		""" Removes a callback for messagees with a specific message id from the network. """
		if not callable(callback):
			raise TypeError()
		if not message_id in self._subscribers:
			raise KeyError()
		
		self._subscribers[message_id].remove(callback)
	
	def on_message(self, message):
		""" Handler for received messages. This method distributes the message to all callbacks. """
		if message.arbitration_id not in self._subscribers:
			return
		
		for callback in self._subscribers[message.arbitration_id]:
			try:
				callback(message)
			except:
				pass


class MessageListener(can.Listener):
	def __init__(self, network):
		if not isinstance(network, Network):
			raise TypeError()
		
		self._network = network
	
	def on_message_received(self, message):
		self._network.on_message(message)
