import threading
import time


class Timer(threading.Thread):
	def __init__(self, function, args = None, kwargs = None):
		"""
		Restartable timer.
		After calling start, it waits ``interval`` seconds and then calls ```function```with ``args`` and ``kwargs```.
		"""
		if not callable(function):
			raise ValueError()
		if args == None:
			args = []
		if kwargs == None:
			kwargs = {}
		
		threading.Thread.__init__(self, daemon = True)
		
		self._interval = 0.0
		self._function = function
		self._args = args
		self._kwargs = kwargs
		
		self._execute_time = 0.0
		self._periodic = threading.Event()
		self._terminate = threading.Event()
		self._trigger_lock = threading.RLock()
		self._trigger = threading.Condition(self._trigger_lock)
		self._condition = threading.Event()
		
		threading.Thread.start(self)
		
		# wait until the timer can be triggered
		self._trigger.acquire()
		self._trigger.release()
	
	def start(self, interval, periodic = False):
		"""
		Triggers the timer and starts a timer cycle. To restart a fresh timer cycle, a call to ``cancel`` followed by a call to ``start`` is needed.
		"""
		if interval <= 0.0:
			raise ValueError()
		if not self._trigger.acquire(False):
			return False
		self._execute_time = time.time() + interval
		self._interval = interval
		if periodic:
			self._periodic.set()
		else:
			self._periodic.clear()
		self._condition.clear()
		self._trigger.notify()
		self._trigger.release()
		return True
	
	def cancel(self):
		"""
		Cancels the current timer cycle.
		"""
		self._periodic.clear()
		self._condition.set()
		# wait until the canceled timer cycle has passed by and a restart is possible
		self._trigger.acquire()
		self._trigger.release()
	
	def run(self):
		self._trigger.acquire()
		while not self._terminate.is_set():
			if not self._periodic.is_set():
				self._trigger.wait()
			self._condition.wait(self._execute_time - time.time())
			if not self._condition.is_set():
				self._function(*self._args, **self._kwargs)
			self._execute_time += self._interval
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
