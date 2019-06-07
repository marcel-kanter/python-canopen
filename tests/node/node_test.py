import unittest
import canopen
import canopen.objectdictionary


class NodeTestCase(unittest.TestCase):
	def test_init(self):
		dictionary = canopen.ObjectDictionary()
		
		with self.assertRaises(ValueError):
			canopen.Node("n", 0, dictionary)
		with self.assertRaises(ValueError):
			canopen.Node("n", 128, dictionary)
		with self.assertRaises(TypeError):
			canopen.Node("n", 1, None)
		
		name = "n"
		node_id = 1
		node = canopen.Node(name, node_id, dictionary)
		
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
		node = canopen.Node("n", 1, dictionary)
		
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
	
	def test_collection(self):
		dictionary = canopen.ObjectDictionary()
		dictionary.append(canopen.objectdictionary.Record("rec", 0x1234))
		dictionary["rec"].append(canopen.objectdictionary.Variable("boolean", 0x1234, 0x01, 0x01, "rw"))
		dictionary["rec"].append(canopen.objectdictionary.Variable("integer8", 0x1234, 0x02, 0x02, "rw"))
		dictionary["rec"].append(canopen.objectdictionary.Variable("integer16", 0x1234, 0x03, 0x03, "rw"))
		dictionary["rec"].append(canopen.objectdictionary.Variable("integer32", 0x1234, 0x04, 0x04, "rw"))
		dictionary["rec"].append(canopen.objectdictionary.Variable("unsigned8", 0x1234, 0x05, 0x05, "r"))
		dictionary["rec"].append(canopen.objectdictionary.Variable("unsigned16", 0x1234, 0x06, 0x06, "w"))
		dictionary["rec"].append(canopen.objectdictionary.Variable("domain", 0x1234, 0x0F, 0x0F, "rw"))
		dictionary["rec"].append(canopen.objectdictionary.Variable("integer24", 0x1234, 0x10, 0x10, "rw"))
		dictionary["rec"].append(canopen.objectdictionary.Variable("integer40", 0x1234, 0x11, 0x11, "rw"))
		dictionary["rec"].append(canopen.objectdictionary.Variable("integer48", 0x1234, 0x12, 0x12, "rw"))
		dictionary.append(canopen.objectdictionary.Variable("var", 0x5678, 0x00, 0x07, "rw"))
		node = canopen.Node("a", 1, dictionary)
		
		# contains
		self.assertFalse("xxx" in node)
		self.assertFalse(99 in node)
		self.assertTrue("rec" in node)
		self.assertTrue(0x1234 in node)
		self.assertTrue("var" in node)
		self.assertTrue(0x5678 in node)
		
		# iter
		items = []
		for k in node:
			items.append(k)
		
		# len
		self.assertEqual(len(node), 2)


if __name__ == "__main__":
	unittest.main()
