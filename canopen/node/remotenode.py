import canopen
from .node import Node


class RemoteNode(Node):
	def __init__(self, name, id):
		Node.__init__(self, name, id)
