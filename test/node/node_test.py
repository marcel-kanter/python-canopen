import unittest
import canopen


class NodeTestCase(unittest.TestCase):
	def test_init(self):
		with self.assertRaises(ValueError):
			node = canopen.Node(0)
		with self.assertRaises(ValueError):
			node = canopen.Node(128)
		
		id = 1
		node = canopen.Node(id)
		
		self.assertEqual(node.id, id)
		
		with self.assertRaises(AttributeError):
			node.id = id


if __name__ == "__main__":
	unittest.main()
