import unittest
import canopen


class NodeTestCase(unittest.TestCase):
	def test_init(self):
		with self.assertRaises(ValueError):
			node = canopen.Node("n", 0)
		with self.assertRaises(ValueError):
			node = canopen.Node("n", 128)
		
		name = "n"
		id = 1
		node = canopen.Node(name, id)
		
		self.assertEqual(node.id, id)
		self.assertEqual(node.name, name)
		
		with self.assertRaises(AttributeError):
			node.id = id
		with self.assertRaises(AttributeError):
			node.name = name


if __name__ == "__main__":
	unittest.main()
