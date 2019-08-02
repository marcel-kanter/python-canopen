import threading


class Timer(threading.Thread):
	def __init__(self, interval, function, args = None, kwargs = None):
		"""
		Restartable timer.
		After calling start, it waits ``interval`` seconds and then calls ```function```with ``args`` and ``kwargs```.
		"""
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
		self._trigger = threading.Condition(threading.Lock())
		self._condition = threading.Event()
		
		threading.Thread.start(self)
	
	def start(self, interval = None):
		"""
		Triggers the timer and starts a timer cycle. To restart a fresh timer cycle, a call to ``cancel`` followed by a call to ``start`` is needed.
		"""
		if not self._trigger.acquire(False):
			return False
		if interval != None:
			self._interval = interval
		self._condition.clear()
		self._trigger.notify()
		self._trigger.release()
		return True
	
	def cancel(self):
		"""
		Cancels the current timer cycle.
		"""
		self._condition.set()
	
	def run(self):
		self._trigger.acquire()
		while not self._terminate.is_set():
			self._trigger.wait()
			self._condition.wait(self._interval)
			if not self._condition.is_set():
				self._function(*self._args, **self._kwargs)
		self._trigger.release()
	
	def stop(self):
		"""
		Cancels the current timer cycle and terminates the timer.
		"""
		self._terminate.set()
		self._condition.set()
		self._trigger.acquire()
		self._trigger.notify()
		self._trigger.release()
