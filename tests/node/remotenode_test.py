import unittest
import canopen


class RemoteNodeTestCase(unittest.TestCase):
	def test_init(self):
		dictionary = canopen.ObjectDictionary()
		
		with self.assertRaises(ValueError):
			canopen.RemoteNode("n", 0, dictionary)
		with self.assertRaises(ValueError):
			canopen.RemoteNode("n", 128, dictionary)
		with self.assertRaises(TypeError):
			canopen.RemoteNode("n", 1, None)
		
		name = "n"
		node_id = 1
		node = canopen.RemoteNode(name, node_id, dictionary)
		
		self.assertEqual(node.dictionary, dictionary)
		self.assertEqual(node.id, node_id)
		self.assertEqual(node.name, name)
		self.assertEqual(node.network, None)
		
		with self.assertRaises(AttributeError):
			node.dictionary = dictionary
		with self.assertRaises(AttributeError):
			node.id = id
		with self.assertRaises(AttributeError):
			node.name = name
		with self.assertRaises(AttributeError):
			node.network = None


if __name__ == "__main__":
	unittest.main()
