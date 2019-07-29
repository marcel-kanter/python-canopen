import threading


class Timer(threading.Thread):
	def __init__(self, interval, function, args = None, kwargs = None):
		if interval < 0:
			raise ValueError()
		if not callable(function):
			raise ValueError()
		if args == None:
			args = []
		if kwargs == None:
			kwargs = {}
		
		threading.Thread.__init__(self)
		
		self._interval = interval
		self._function = function
		self._args = args
		self._kwargs = kwargs
		
		self._terminate = threading.Event()
		self._trigger = threading.Event()
		self._condition = threading.Event()
		
		threading.Thread.start(self)
	
	def start(self, interval = None):
		if interval != None:
			self._interval = interval
		self._trigger.set()
	
	def run(self):
		self._trigger.wait()
		self._trigger.clear()
		while not self._terminate.is_set():
			self._condition.wait(self._interval)
			if not self._condition.is_set():
				self._function(*self._args, **self._kwargs)
			self._trigger.wait()
			self._trigger.clear()
	
	def stop(self):
		self._terminate.set()
		self._condition.set()
		self._trigger.set()
