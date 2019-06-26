import unittest
import canopen.objectdictionary
import canopen.node


class RecordTestCase(unittest.TestCase):
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
			canopen.node.record.Record(dictionary, dictionary["rec"])
		with self.assertRaises(TypeError):
			canopen.node.record.Record(node, node)
		with self.assertRaises(TypeError):
			canopen.node.record.Record(node, dictionary["arr"])
		with self.assertRaises(TypeError):
			canopen.node.record.Record(node, dictionary["var"])
		
		#### Test step: property forwarding
		self.assertEqual(node["rec"].name, dictionary["rec"].name)
		self.assertEqual(node["rec"].index, dictionary["rec"].index)
	
	def test_collection(self):
		dictionary = canopen.ObjectDictionary()
		dictionary.append(canopen.objectdictionary.Record("rec", 0xabcd))
		dictionary["rec"].append(canopen.objectdictionary.Variable("first", 0xabcd, 0x01, 0x02, "rw"))
		dictionary["rec"].append(canopen.objectdictionary.Variable("second", 0xabcd, 0x02, 0x02, "rw"))
		
		node = canopen.Node("n", 1, dictionary)
		
		record = canopen.node.record.Record(node, dictionary["rec"])
		
		# contains
		self.assertFalse("xxx" in record)
		self.assertFalse(99 in record)
		self.assertTrue("first" in record)
		self.assertTrue(0x01 in record)
		self.assertTrue("second" in record)
		self.assertTrue(0x02 in record)
		
		# iter, getitem
		items = []
		for k in record:
			items.append(record[k])
		
		# len
		self.assertEqual(len(record), len(dictionary["rec"]))
		self.assertEqual(len(record), len(items))


if __name__ == "__main__":
	unittest.main()
