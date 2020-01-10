import collections
import can
import canopen


class Network(collections.abc.Collection):
	""" Representation of a CANopen network.
	
	This class is the representation of one CANopen network. It is a mutable auto-associative mapping and may contain zero or more CANopen nodes.

	To use Network together with a CAN bus, first the CAN bus instance must be created and then the network attached to the bus.
	In the end, the network may be detached from the CAN bus.
	"""
	def __init__(self):
		""" Initialises a ``Network``
		"""
		self._bus = None
		self._listeners = [MessageListener(self)]
		self._notifier = None
		self._subscribers = {}
		
		self._items_id = {}
		self._items_name = {}
	
	def __contains__(self, key):
		""" Returns True if the network contains a node with the specified name or id
		
		:param key: The name or identifier to look for
		
		:returns: True if a node is in the network with the given name or identifier
		"""
		try:
			self[key]
		except:
			return False
		else:
			return True
	
	def __iter__(self):
		""" Returns an iterator over all nodes in the network.
		"""
		return iter(self._items_id.values())
	
	def __len__(self):
		""" Returns the number of nodes in the network.
		"""
		return len(self._items_id)
	
	def __getitem__(self, key):
		""" Returns the node identified by the name or the id.
		Raises KeyError if there is no node in the network with the given name or identifier.
		
		:param key: The name or identifier to look for
		
		:returns: A ``Node`` object
		
		:raises: KeyError
		"""
		if key in self._items_id:
			return self._items_id[key]
		if key in self._items_name:
			return self._items_name[key]
		raise KeyError()
	
	def __delitem__(self, key):
		""" Removes a node identified by the name of the id from the network.
		Raises KeyError if there is no node in the network with the given name or identifier.
		
		:param key: The name or identifier of the node to remove
		
		:raises: KeyError
		"""
		item = self[key]
		item.detach()
		del self._items_id[item.id]
		del self._items_name[item.name]
	
	def add(self, node):
		""" Adds a node to the network. It may be accessed later by the name or the id.
		Raises TypeError if the node is not a subclass of canopen.Node.
		Raises ValueError if a node with the name or the identifier is already in the network.
		Raises RuntimeError if the identifier of the node is 255.
		
		:param node: The node to add
		
		:raises: RuntimeError, TypeError, ValueError
		"""
		if not isinstance(node, canopen.Node):
			raise TypeError()
		if node.id in self._items_id or node.name in self._items_name:
			raise ValueError()
		if node.id == 255:
			raise RuntimeError()
		
		node.attach(self)
		self._items_id[node.id] = node
		self._items_name[node.name] = node
	
	def attach(self, bus, builtin_notifier = True):
		""" Attach the network to a CAN bus.
		Raises TypeError if the bus is not a subclass of can.BusABC
		Raises ValueError if the network is already attached to the bus.
		
		:param bus: The can bus to connect.
		
		:param builtin_notifier: Use the builtin notifier or not. If False, all (relevant) CAN messages must be passed to on_message.
		
		:raises: TypeError, ValueError
		"""
		if not isinstance(bus, can.BusABC):
			raise TypeError()
		if self._bus == bus:
			raise ValueError()
		if self.is_attached():
			self.detach()
		
		self._bus = bus
		if builtin_notifier:
			self._notifier = can.Notifier(self._bus, self._listeners)
	
	def detach(self):
		""" Detach the network from a CAN bus.
		Raises RuntimeError if the network is not attached to a bus.
		
		:raises: RuntimeError
		"""
		if not self.is_attached():
			raise RuntimeError()
		
		if self._notifier != None:
			self._notifier.stop()
			self._notifier = None
		self._bus = None
	
	def is_attached(self):
		""" Returns True when the ``Network`` is attached to a bus.
		"""
		return self._bus != None
	
	def send(self, message):
		""" Sends a CAN message on the CAN bus.
		Raises RuntimeError if the network is not attached to a bus.
		
		:param message: The message to send.
		
		:raises: RuntimeError
		"""
		if not self.is_attached():
			raise RuntimeError()
		
		self._bus.send(message)
	
	def subscribe(self, callback, message_id):
		""" Adds a callback for messages with a specific message id to the network.
		Raises TypeError if callback is not callable
		
		:param callback: The function to call with the matching messages.
		
		:param message_id: The identifier of the messages for which the callback should be called.
		
		:raises: TypeError
		"""
		if not callable(callback):
			raise TypeError()
		
		message_id = int(message_id)
		
		if message_id not in self._subscribers:
			self._subscribers[message_id] = []
		self._subscribers[message_id].append(callback)
	
	def unsubscribe(self, callback, message_id):
		""" Removes a callback for messagees with a specific message id from the network.
		Raises KeyError if there are no callbacks for the message identifier.
		Raises ValueError if the callback is not in the list of callbacks for the message identifier.
		
		:param callback: The function to remove from the list of callbacks
		
		:param message_id: The identifier of the messages.
		
		:raises: KeyError, ValueError
		"""		
		self._subscribers[message_id].remove(callback)
	
	def on_message(self, message):
		""" Handler for received messages.
		This method distributes the message to the callbacks. All (relevant) message must be passed to this handler if ``Network.attach`` was called with ``builtin_notifier`` set to ``False``.
		"""
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
