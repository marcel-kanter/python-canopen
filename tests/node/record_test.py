import unittest
import canopen.objectdictionary
import canopen.node


class RecordTestCase(unittest.TestCase):
	def test_init(self):
		dictionary = canopen.ObjectDictionary()
		dictionary.add(canopen.objectdictionary.DefStruct("defstruct", 0x40))
		dictionary["defstruct"].add(canopen.objectdictionary.Variable("first", 0x40, 0x00, canopen.objectdictionary.UNSIGNED8, "ro"))
		dictionary.add(canopen.objectdictionary.DefType("deftype", 0x60))
		dictionary.add(canopen.objectdictionary.Record("rec", 0x1234, 0x00))
		dictionary["rec"].description = "Lorem ipsum dolor"
		dictionary["rec"].add(canopen.objectdictionary.Variable("boolean", 0x1234, 0x01, 0x01, "rw"))
		dictionary["rec"].add(canopen.objectdictionary.Variable("integer8", 0x1234, 0x02, 0x02, "rw"))
		dictionary["rec"].add(canopen.objectdictionary.Variable("integer16", 0x1234, 0x03, 0x03, "rw"))
		dictionary["rec"].add(canopen.objectdictionary.Variable("integer32", 0x1234, 0x04, 0x04, "rw"))
		dictionary["rec"].add(canopen.objectdictionary.Variable("unsigned8", 0x1234, 0x05, 0x05, "ro"))
		dictionary["rec"].add(canopen.objectdictionary.Variable("unsigned16", 0x1234, 0x06, 0x06, "wo"))
		dictionary["rec"].add(canopen.objectdictionary.Variable("domain", 0x1234, 0x0F, 0x0F, "rw"))
		dictionary["rec"].add(canopen.objectdictionary.Variable("integer24", 0x1234, 0x10, 0x10, "rw"))
		dictionary["rec"].add(canopen.objectdictionary.Variable("integer40", 0x1234, 0x11, 0x11, "rw"))
		dictionary["rec"].add(canopen.objectdictionary.Variable("integer48", 0x1234, 0x12, 0x12, "rw"))
		dictionary.add(canopen.objectdictionary.Variable("var", 0x5678, 0x00, 0x07, "rw"))
		dictionary.add(canopen.objectdictionary.Array("arr", 0xabcd, canopen.objectdictionary.INTEGER8))
		dictionary["arr"].description = "Gallia est omnis divisa in partes tres"
		dictionary["arr"].add(canopen.objectdictionary.Variable("first", 0xabcd, 0x01, canopen.objectdictionary.INTEGER8, "rw"))
		dictionary["arr"].add(canopen.objectdictionary.Variable("second", 0xabcd, 0x02, canopen.objectdictionary.INTEGER8, "rw"))
		
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
		self.assertEqual(node["rec"].object_type, dictionary["rec"].object_type)
		self.assertEqual(node["rec"].name, dictionary["rec"].name)
		self.assertEqual(node["rec"].index, dictionary["rec"].index)
		self.assertEqual(node["rec"].data_type, dictionary["rec"].data_type)
		self.assertEqual(node["rec"].description, dictionary["rec"].description)
	
	def test_collection(self):
		dictionary = canopen.ObjectDictionary()
		dictionary.add(canopen.objectdictionary.Record("rec", 0xabcd, 0x00))
		dictionary["rec"].add(canopen.objectdictionary.Variable("first", 0xabcd, 0x01, 0x02, "rw"))
		dictionary["rec"].add(canopen.objectdictionary.Variable("second", 0xabcd, 0x02, 0x02, "rw"))
		
		node = canopen.Node("n", 1, dictionary)
		
		examinee = canopen.node.record.Record(node, dictionary["rec"])
		
		# contains
		self.assertFalse("xxx" in examinee)
		self.assertFalse(99 in examinee)
		self.assertTrue("first" in examinee)
		self.assertTrue(0x01 in examinee)
		self.assertTrue("second" in examinee)
		self.assertTrue(0x02 in examinee)
		
		# getitem
		item = examinee["first"]
		self.assertTrue(item.name in examinee)
		
		# iter
		items = []
		for k in examinee:
			items.append(k)
		
		# len
		self.assertEqual(len(examinee), len(dictionary["rec"]))
		self.assertEqual(len(examinee), len(items))


if __name__ == "__main__":
	unittest.main()
