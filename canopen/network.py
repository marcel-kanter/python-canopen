class Network(object):
	def __init__(self):
		self._bus = None
	
	def connect(self, bus):
		if self._bus != None:
			self.disconnect()
		
		self._bus = bus
	
	def disconnect(self):
		self._bus = None
