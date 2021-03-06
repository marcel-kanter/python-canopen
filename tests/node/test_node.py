import unittest
import canopen.objectdictionary
from unittest.mock import MagicMock


class NodeTestCase(unittest.TestCase):
	def test_init(self):
		dictionary = canopen.ObjectDictionary()
		
		with self.assertRaises(ValueError):
			canopen.Node("n", 0, dictionary)
		with self.assertRaises(ValueError):
			canopen.Node("n", 128, dictionary)
		with self.assertRaises(TypeError):
			canopen.Node("n", 1, None)
		
		test_data = [("xyz", 1), ("abc", 255)]
		for name, node_id in test_data:
			node = canopen.Node(name, node_id, dictionary)
			
			self.assertEqual(node.dictionary, dictionary)
			self.assertEqual(node.id, node_id)
			self.assertEqual(node.name, name)
			self.assertEqual(node.network, None)
			
			with self.assertRaises(AttributeError):
				node.dictionary = dictionary
			with self.assertRaises(ValueError):
				node.id = -1
			with self.assertRaises(ValueError):
				node.id = 128
			with self.assertRaises(AttributeError):
				node.name = name
			with self.assertRaises(AttributeError):
				node.network = None
	
	def test_equals(self):
		dictionary = canopen.ObjectDictionary()
		a = canopen.Node("a", 1, dictionary)
		
		#### Test step: Reflexivity
		self.assertTrue(a == a)
		
		#### Test step: Compare same classes only (required for transitivity)
		test_data = [None, 3, canopen.LocalNode("a", 1, dictionary)]
		for value in test_data:
			with self.subTest("value=" + str(value)):
				self.assertFalse(a == value)
		
		#### Test step: Consistency
		b = canopen.Node("a", 1, dictionary)
		for _ in range(3):
			self.assertTrue(a == b)
		
		#### Test step: Symmetricality
		b = canopen.Node("a", 1, dictionary)
		self.assertTrue(a == b)
		self.assertEqual(a == b, b == a)
	
	def test_attach_detach(self):
		network1 = canopen.Network()
		network2 = canopen.Network()
		dictionary = canopen.ObjectDictionary()
		node = canopen.Node("n", 1, dictionary)
		
		with self.assertRaises(RuntimeError):
			node.detach()
		
		with self.assertRaises(TypeError):
			node.attach(None)
			
		self.assertFalse(node.is_attached())
		
		# Attaching a node with an unassigned node id is impossible
		node.id = 255
		self.assertEqual(node.id, 255)
		
		with self.assertRaises(RuntimeError):
			node.attach(network1)
		
		# Change the node id to 10 and attach
		node.id = 10
		self.assertEqual(node.id, 10)
		
		node.attach(network1)
		self.assertTrue(node.is_attached())
		self.assertEqual(node.network, network1)
		
		# Changing the node id when the node is attached
		with self.assertRaises(RuntimeError):
			node.id = 1
		
		with self.assertRaises(ValueError):
			node.attach(network1)
		
		node.attach(network2)
		self.assertTrue(node.is_attached())
		self.assertEqual(node.network, network2)
		
		node.detach()
		self.assertFalse(node.is_attached())
		
		node.id = 255
		self.assertEqual(node.id, 255)
		
		node.id = 127
		self.assertEqual(node.id, 127)
	
	def test_collection(self):
		dictionary = canopen.ObjectDictionary()
		dictionary.add(canopen.objectdictionary.DefStruct("defstruct", 0x40))
		dictionary["defstruct"].add(canopen.objectdictionary.Variable("first", 0x40, 0x00, canopen.objectdictionary.UNSIGNED8, "ro"))
		dictionary.add(canopen.objectdictionary.DefType("deftype", 0x60))
		dictionary.add(canopen.objectdictionary.DefType("domain", 0x1000))
		dictionary.add(canopen.objectdictionary.Record("rec", 0x1234, 0x00))
		dictionary["rec"].add(canopen.objectdictionary.Variable("boolean", 0x1234, 0x01, canopen.objectdictionary.BOOLEAN, "rw"))
		dictionary["rec"].add(canopen.objectdictionary.Variable("integer8", 0x1234, 0x02, canopen.objectdictionary.INTEGER8, "rw"))
		dictionary["rec"].add(canopen.objectdictionary.Variable("integer16", 0x1234, 0x03, canopen.objectdictionary.INTEGER16, "rw"))
		dictionary["rec"].add(canopen.objectdictionary.Variable("integer32", 0x1234, 0x04, canopen.objectdictionary.INTEGER32, "rw"))
		dictionary["rec"].add(canopen.objectdictionary.Variable("unsigned8", 0x1234, 0x05, canopen.objectdictionary.UNSIGNED8, "ro"))
		dictionary["rec"].add(canopen.objectdictionary.Variable("unsigned16", 0x1234, 0x06, canopen.objectdictionary.UNSIGNED16, "wo"))
		dictionary["rec"].add(canopen.objectdictionary.Variable("domain", 0x1234, 0x0F, canopen.objectdictionary.DOMAIN, "rw"))
		dictionary["rec"].add(canopen.objectdictionary.Variable("integer24", 0x1234, 0x10, canopen.objectdictionary.INTEGER24, "rw"))
		dictionary["rec"].add(canopen.objectdictionary.Variable("real64", 0x1234, 0x11, canopen.objectdictionary.REAL64, "rw"))
		dictionary["rec"].add(canopen.objectdictionary.Variable("integer40", 0x1234, 0x12, canopen.objectdictionary.INTEGER40, "rw"))
		dictionary.add(canopen.objectdictionary.Variable("var", 0x5678, 0x00, canopen.objectdictionary.UNSIGNED32, "rw"))
		dictionary.add(canopen.objectdictionary.Array("arr", 0xabcd, canopen.objectdictionary.INTEGER8))
		dictionary["arr"].add(canopen.objectdictionary.Variable("first", 0xabcd, 0x01, canopen.objectdictionary.INTEGER8, "rw"))
		dictionary["arr"].add(canopen.objectdictionary.Variable("second", 0xabcd, 0x02, canopen.objectdictionary.INTEGER8, "rw"))
		
		node = canopen.Node("a", 1, dictionary)
		
		#### Test step: contains
		self.assertFalse("xxx" in node)
		self.assertFalse(0x99 in node)
		self.assertTrue("deftype" in node)
		self.assertTrue(0x40 in node)
		self.assertTrue("defstruct" in node)
		self.assertTrue(0x60 in node)
		self.assertTrue("domain" in node)
		self.assertTrue(0x1000 in node)
		self.assertTrue("rec" in node)
		self.assertTrue(0x1234 in node)
		self.assertTrue("var" in node)
		self.assertTrue(0x5678 in node)
		
		#### Test step: iter, getitem, len
		with self.assertRaises(KeyError):
			node[0x99]
		
		items = []
		for k in node:
			items.append(k)
		
		self.assertEqual(len(node), len(items))
		self.assertEqual(len(node), len(dictionary))
		
		#### Test step: ObjectDictionary.__getitem__ returns a type that node.__getitem__ doesn't know -> this should raise NotImplementedError
		# prepare a mocked dictionary and let it return None
		mockdictionary = MagicMock(spec = canopen.ObjectDictionary)
		mockdictionary.__contains__.side_effect = dictionary.__contains__
		mockdictionary.__iter__.side_effect = dictionary.__iter__
		mockdictionary.__len__.side_effect = dictionary.__len__
		mockdictionary.__getitem__.side_effect = self.__return_value
		
		node = canopen.Node("a", 1, mockdictionary)
		
		# mocked getitem will return a str, which is not a valid entry in the object dictionary
		with self.assertRaises(NotImplementedError):
			node["ZZZ"]
	
	def test_data_access(self):
		dictionary = canopen.ObjectDictionary()
		dictionary.add(canopen.objectdictionary.Record("rec", 0x1234, 0x00))
		dictionary["rec"].add(canopen.objectdictionary.Variable("integer32", 0x1234, 0x04, canopen.objectdictionary.INTEGER32, "rw"))
		dictionary.add(canopen.objectdictionary.Variable("var", 0x5678, 0x00, canopen.objectdictionary.UNSIGNED32, "rw"))
		examinee = canopen.Node("n", 1, dictionary)
		
		#### Test step: get_data and set_data not implemented
		with self.assertRaises(NotImplementedError):
			examinee.get_data(0x5678, 0x00)
		with self.assertRaises(NotImplementedError):
			examinee.set_data(0x5678, 0x00, 0x00)
	
	def __return_value(self, value):
		return value


if __name__ == "__main__":
	unittest.main()
