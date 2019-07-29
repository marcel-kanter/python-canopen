import threading


class Timer(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		
		self._terminate = threading.Event()
		self._trigger = threading.Event()
		
		threading.Thread.start(self)
	
	def start(self):
		self._trigger.set()
	
	def run(self):
		self._trigger.wait()
		self._trigger.clear()
		while not self._terminate.is_set():
			self._trigger.wait()
			self._trigger.clear()
	
	def stop(self):
		self._terminate.set()
		self._trigger.set()
