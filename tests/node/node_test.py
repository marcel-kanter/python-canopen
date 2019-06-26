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
		dictionary.append(canopen.objectdictionary.DefStruct("defstruct", 0x40))
		dictionary["defstruct"].append(canopen.objectdictionary.Variable("first", 0x40, 0x00, 0x05, "ro"))
		dictionary.append(canopen.objectdictionary.DefType("deftype", 0x60))
		dictionary.append(canopen.objectdictionary.Record("rec", 0x1234))
		dictionary["rec"].append(canopen.objectdictionary.Variable("boolean", 0x1234, 0x01, 0x01, "rw"))
		dictionary["rec"].append(canopen.objectdictionary.Variable("integer8", 0x1234, 0x02, 0x02, "rw"))
		dictionary["rec"].append(canopen.objectdictionary.Variable("integer16", 0x1234, 0x03, 0x03, "rw"))
		dictionary["rec"].append(canopen.objectdictionary.Variable("integer32", 0x1234, 0x04, 0x04, "rw"))
		dictionary["rec"].append(canopen.objectdictionary.Variable("unsigned8", 0x1234, 0x05, 0x05, "ro"))
		dictionary["rec"].append(canopen.objectdictionary.Variable("unsigned16", 0x1234, 0x06, 0x06, "wo"))
		dictionary["rec"].append(canopen.objectdictionary.Variable("domain", 0x1234, 0x0F, 0x0F, "rw"))
		dictionary["rec"].append(canopen.objectdictionary.Variable("integer24", 0x1234, 0x10, 0x10, "rw"))
		dictionary["rec"].append(canopen.objectdictionary.Variable("integer40", 0x1234, 0x11, 0x11, "rw"))
		dictionary["rec"].append(canopen.objectdictionary.Variable("integer48", 0x1234, 0x12, 0x12, "rw"))
		dictionary.append(canopen.objectdictionary.Variable("var", 0x5678, 0x00, 0x07, "rw"))
		dictionary.append(canopen.objectdictionary.Array("arr", 0xabcd))
		
		node = canopen.Node("a", 1, dictionary)
		
		#### Test step: contains
		self.assertFalse("xxx" in node)
		self.assertFalse(0x99 in node)
		self.assertTrue("deftype" in node)
		self.assertTrue(0x40 in node)
		self.assertTrue("defstruct" in node)
		self.assertTrue(0x60 in node)
		self.assertTrue("rec" in node)
		self.assertTrue(0x1234 in node)
		self.assertTrue("var" in node)
		self.assertTrue(0x5678 in node)
		
		#### Test step: iter, getitem, len
		with self.assertRaises(KeyError):
			node[0x99]
		
		items = []
		for k in node:
			items.append(node[k])
		
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
	
	def __return_value(self, value):
		return value


if __name__ == "__main__":
	unittest.main()
