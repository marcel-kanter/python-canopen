from .service import Service


class SDOServer(Service):
	def __init__(self):
		Service.__init__(self)
	
	def attach(self, node):
		Service.attach(self, node)
	
	def detach(self):
		Service.detach(self)
