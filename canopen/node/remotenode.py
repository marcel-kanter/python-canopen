from .node import Node


class RemoteNode(Node):
	""" Representation of a remote CANopen node.
	
	This class represents a remote CANopen node and can be used to access other nodes on the bus. It is an auto-associative list and may contain zero or more variables, records or arrays.
	"""
	def __init__(self, name, node_id, dictionary):
		Node.__init__(self, name, node_id, dictionary)
