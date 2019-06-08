import unittest
import canopen.objectdictionary
import canopen.node


class VariableTestCase(unittest.TestCase):
	def test_init(self):
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
		dictionary.append(canopen.objectdictionary.Array("arr", 0xabcd))
		dictionary["arr"].append(canopen.objectdictionary.Variable("first", 0xabcd, 0x01, 0x02, "rw"))
		dictionary["arr"].append(canopen.objectdictionary.Variable("second", 0xabcd, 0x02, 0x02, "rw"))
		
		node = canopen.Node("n", 1, dictionary)
		
		with self.assertRaises(TypeError):
			canopen.node.variable.Variable(dictionary, dictionary["var"])
		with self.assertRaises(TypeError):
			canopen.node.variable.Variable(node, node)
		with self.assertRaises(TypeError):
			canopen.node.variable.Variable(node, dictionary["rec"])
		with self.assertRaises(TypeError):
			canopen.node.variable.Variable(node, dictionary["arr"])
		
		#### Test step: property forwarding
		self.assertEqual(node["var"].name, dictionary["var"].name)
		self.assertEqual(node["var"].index, dictionary["var"].index)
		self.assertEqual(node["var"].subindex, dictionary["var"].subindex)
		self.assertEqual(node["var"].data_type, dictionary["var"].data_type)
		self.assertEqual(node["var"].access_type, dictionary["var"].access_type)


if __name__ == "__main__":
	unittest.main()
