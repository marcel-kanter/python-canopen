import threading


class Timer(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self._terminate = threading.Event()
		threading.Thread.start(self)
	
	def run(self):
		while not self._terminate.is_set():
			self._terminate.wait()
	
	def stop(self):
		self._terminate.set()
