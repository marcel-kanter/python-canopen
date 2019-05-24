import can
import canopen.node


class Network(object):
	def __init__(self):
		self._bus = None
		self._listeners = [MessageListener(self)]
		self._notifier = None
		self._subscribers = {}
		
		self._items_id = {}
		self._items_name = {}
	
	def __contains__(self, key):
		try:
			self[key]
		except:
			return False
		else:
			return True
	
	def __iter__(self):
		return iter(self._items_id)
	
	def __len__(self):
		return len(self._items_id)
	
	def __getitem__(self, key):
		if key in self._items_id:
			return self._items_id[key]
		if key in self._items_name:
			return self._items_name[key]
		raise KeyError()
	
	def __delitem__(self, key):
		item = self[key]
		item.detach()
		del self._items_id[item.id]
		del self._items_name[item.name]
	
	def append(self, value):
		if not isinstance(value, canopen.Node):
			raise TypeError()
		if value.id in self._items_id or value.name in self._items_name:
			raise ValueError()
		
		self._items_id[value.id] = value
		self._items_name[value.name] = value
		value.attach(self)
	
	def attach(self, bus):
		if self._bus != None:
			self.detach()
		
		self._bus = bus
		self._notifier = can.Notifier(self._bus, self._listeners)
	
	def detach(self):
		if self._notifier != None:
			self._notifier.stop()
		self._notifier = None
		self._bus = None
	
	def subscribe(self, callback, message_id):
		if not callable(callback):
			raise TypeError()
		
		if message_id not in self._subscribers:
			self._subscribers[message_id] = []
		self._subscribers[message_id].append(callback)
	
	def unsubscribe(self, callback, message_id):
		if not callable(callback):
			raise TypeError()
		if not message_id in self._subscribers:
			raise KeyError()
		
		self._subscribers[message_id].remove(callback)
	
	def on_message(self, message):
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
