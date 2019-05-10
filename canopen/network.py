import can


class Network(object):
	def __init__(self):
		self._bus = None
		self._listeners = [MessageListener(self)]
		self._notifier = None
		self._subscribers = {}
	
	def connect(self, bus):
		if self._bus != None:
			self.disconnect()
		
		self._bus = bus
		self._notifier = can.Notifier(self._bus, self._listeners)
	
	def disconnect(self):
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
