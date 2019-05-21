import unittest
import canopen


class LocalNodeTestCase(unittest.TestCase):
	def test_init(self):
		with self.assertRaises(ValueError):
			canopen.LocalNode("n", 0)
		with self.assertRaises(ValueError):
			canopen.LocalNode("n", 128)
		
		name = "n"
		node_id = 1
		node = canopen.LocalNode(name, node_id)
		
		self.assertEqual(node.id, node_id)
		self.assertEqual(node.name, name)
		self.assertEqual(node.network, None)
		
		with self.assertRaises(AttributeError):
			node.id = node_id
		with self.assertRaises(AttributeError):
			node.name = name
		with self.assertRaises(AttributeError):
			node.network = None


if __name__ == "__main__":
	unittest.main()
