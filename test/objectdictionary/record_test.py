import unittest
import canopen


class RecordTestCase(unittest.TestCase):
	def test_init(self):
		with self.assertRaises(ValueError):
			record = canopen.objectdictionary.Record("rec", -1)
		with self.assertRaises(ValueError):
			record = canopen.objectdictionary.Record("rec", 65536)
		
		name = "rec"
		index = 100
		record = canopen.objectdictionary.Record(name, index)
		
		self.assertEqual(record.name, name)
		self.assertEqual(record.index, index)
		
		with self.assertRaises(AttributeError):
			record.name = name
		with self.assertRaises(AttributeError):
			record.index = index
	
	def test_collection(self):
		record = canopen.objectdictionary.Record("rec", 100)
		
		# append
		x = canopen.objectdictionary.Array("arr", 200)
		with self.assertRaises(TypeError):
			record.append(x)
		
		x = canopen.objectdictionary.Record("rec", 300)
		with self.assertRaises(TypeError):
			record.append(x)
		
		x = canopen.objectdictionary.Variable("var", 200, 0)
		with self.assertRaises(ValueError):
			record.append(x)
		
		v1 = canopen.objectdictionary.Variable("var1", 100, 0)
		record.append(v1)
		self.assertEqual(len(record), 1)
		
		x = canopen.objectdictionary.Variable("var1", 100, 1)
		with self.assertRaises(ValueError):
			record.append(x)
		x = canopen.objectdictionary.Variable("rec", 100, 0)
		with self.assertRaises(ValueError):
			record.append(x)
		
		v2 = canopen.objectdictionary.Variable("var2", 100, 1)
		record.append(v2)
		self.assertEqual(len(record), 2)
		
		# contains
		self.assertFalse("xxx" in record)
		self.assertFalse(999 in record)
		self.assertTrue(v1.name in record)
		self.assertTrue(v1.subindex in record)
		self.assertTrue(v2.name in record)
		self.assertTrue(v2.subindex in record)
		
		# iter, getitem
		items = []
		for k in record:
			items.append(record[k])
		
		# delitem
		for x in items:
			del record[x.name]
		
		self.assertEqual(len(record), 0)


if __name__ == "__main__":
	unittest.main()
