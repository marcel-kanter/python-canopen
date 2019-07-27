import unittest
import canopen.objectdictionary
import canopen.node


class DefTypeTestCase(unittest.TestCase):
	def test_init(self):
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
		dictionary["arr"].append(canopen.objectdictionary.Variable("first", 0xabcd, 0x01, 0x02, "rw"))
		dictionary["arr"].append(canopen.objectdictionary.Variable("second", 0xabcd, 0x02, 0x02, "rw"))
		
		node = canopen.Node("n", 1, dictionary)
		
		with self.assertRaises(TypeError):
			canopen.node.deftype.DefType(dictionary, dictionary["deftype"])
		with self.assertRaises(TypeError):
			canopen.node.deftype.DefType(node, node)
		with self.assertRaises(TypeError):
			canopen.node.deftype.DefType(node, dictionary["rec"])
		with self.assertRaises(TypeError):
			canopen.node.deftype.DefType(node, dictionary["arr"])
		
		canopen.node.deftype.DefType(node, dictionary["deftype"])
		
		#### Test step: property forwarding
		self.assertEqual(node["deftype"].object_type, dictionary["deftype"].object_type)
		self.assertEqual(node["deftype"].name, dictionary["deftype"].name)
		self.assertEqual(node["deftype"].index, dictionary["deftype"].index)
		self.assertEqual(node["deftype"].subindex, dictionary["deftype"].subindex)
		self.assertEqual(node["deftype"].data_type, dictionary["deftype"].data_type)
		self.assertEqual(node["deftype"].access_type, dictionary["deftype"].access_type)


if __name__ == "__main__":
	unittest.main()
