import canopen
from .node import Node


class LocalNode(Node):
	def __init__(self, name, id):
		super(LocalNode, self).__init__(name, id)
