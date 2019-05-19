import unittest
import canopen


class RemoteNodeTestCase(unittest.TestCase):
	def test_init(self):
		with self.assertRaises(ValueError):
			node = canopen.RemoteNode("n", 0)
		with self.assertRaises(ValueError):
			node = canopen.RemoteNode("n", 128)
		
		name = "n"
		id = 1
		node = canopen.RemoteNode(name, id)
		
		self.assertEqual(node.id, id)
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
