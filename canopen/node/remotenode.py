import canopen
from .node import Node


class RemoteNode(Node):
	def __init__(self, name, id):
		super(RemoteNode, self).__init__(name, id)
