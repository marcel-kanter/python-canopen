import unittest
import canopen


class LocalNodeTestCase(unittest.TestCase):
	def test_init(self):
		dictionary = canopen.ObjectDictionary()
		
		with self.assertRaises(ValueError):
			canopen.LocalNode("n", 0, dictionary)
		with self.assertRaises(ValueError):
			canopen.LocalNode("n", 128, dictionary)
		with self.assertRaises(TypeError):
			canopen.LocalNode("n", 1, None)
		
		name = "n"
		node_id = 1
		node = canopen.LocalNode(name, node_id, dictionary)
		
		self.assertEqual(node.dictionary, dictionary)
		self.assertEqual(node.id, node_id)
		self.assertEqual(node.name, name)
		self.assertEqual(node.network, None)
		
		with self.assertRaises(AttributeError):
			node.dictionary = dictionary
		with self.assertRaises(AttributeError):
			node.id = node_id
		with self.assertRaises(AttributeError):
			node.name = name
		with self.assertRaises(AttributeError):
			node.network = None

	def test_attach_detach(self):
		network1 = canopen.Network()
		network2 = canopen.Network()
		dictionary = canopen.ObjectDictionary()
		node = canopen.LocalNode("n", 1, dictionary)
		
		with self.assertRaises(RuntimeError):
			node.detach()
		
		with self.assertRaises(TypeError):
			node.attach(None)
		
		node.attach(network1)
		
		self.assertEqual(node.network, network1)
		
		with self.assertRaises(ValueError):
			node.attach(network1)
		
		node.attach(network2)
		
		self.assertEqual(node.network, network2)
		
		node.detach()

if __name__ == "__main__":
	unittest.main()
