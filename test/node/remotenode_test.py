import unittest
import canopen


class RemoteNodeTestCase(unittest.TestCase):
	def test_init(self):
		with self.assertRaises(ValueError):
			canopen.RemoteNode("n", 0)
		with self.assertRaises(ValueError):
			canopen.RemoteNode("n", 128)
		
		name = "n"
		node_id = 1
		node = canopen.RemoteNode(name, node_id)
		
		self.assertEqual(node.id, node_id)
		self.assertEqual(node.name, name)
		self.assertEqual(node.network, None)
		
		with self.assertRaises(AttributeError):
			node.id = id
		with self.assertRaises(AttributeError):
			node.name = name
		with self.assertRaises(AttributeError):
			node.network = None


if __name__ == "__main__":
	unittest.main()
