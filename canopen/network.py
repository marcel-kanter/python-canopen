import can


class Network(object):
	def __init__(self):
		self._bus = None
		self._listeners = [MessageListener(self)]
		self._notifier = None
	
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
	
	def on_message(self, message):
		pass


class MessageListener(can.Listener):
	def __init__(self, network):
		if not isinstance(network, Network):
			raise TypeError()
		
		self._network = network
	
	def on_message_received(self, message):
		self._network.on_message(message)
