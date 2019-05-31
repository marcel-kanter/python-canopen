from .node import Node


class RemoteNode(Node):
	def __init__(self, name, node_id, dictionary):
		Node.__init__(self, name, node_id, dictionary)
