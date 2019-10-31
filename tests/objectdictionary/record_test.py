import unittest
import canopen.objectdictionary


class RecordTestCase(unittest.TestCase):
	def test_init(self):
		with self.assertRaises(ValueError):
			canopen.objectdictionary.Record("rec", -1, 0x00)
		with self.assertRaises(ValueError):
			canopen.objectdictionary.Record("rec", 65536, 0x00)
		with self.assertRaises(ValueError):
			canopen.objectdictionary.Record("rec", 0, -1)
		with self.assertRaises(ValueError):
			canopen.objectdictionary.Record("rec", 0, 65536)
		
		name = "rec"
		index = 100
		data_type = canopen.objectdictionary.UNSIGNED32
		record = canopen.objectdictionary.Record(name, index, data_type)
		
		self.assertEqual(record.object_type, 9)
		self.assertEqual(record.name, name)
		self.assertEqual(record.index, index)
		self.assertEqual(record.data_type, data_type)
		
		with self.assertRaises(AttributeError):
			record.name = name
		with self.assertRaises(AttributeError):
			record.index = index
		with self.assertRaises(AttributeError):
			record.data_type = data_type
	
	def test_equals(self):
		a = canopen.objectdictionary.Record("rec", 100, 0x00)
		
		#### Test step: Reflexivity
		self.assertTrue(a == a)
		
		#### Test step: Compare same classes only (required for transitivity)
		test_data = [None, 3, canopen.objectdictionary.DefStruct("rec", 100)]
		for value in test_data:
			with self.subTest("value=" + str(value)):
				self.assertFalse(a == value)
		
		#### Test step: Consistency
		b = canopen.objectdictionary.Record("rec", 100, 0x00)
		for _ in range(3):
			self.assertTrue(a == b)
		
		#### Test step: Symmetricality, Contents
		b = canopen.objectdictionary.Record("rec", 100, 0x00)
		self.assertTrue(a == b)
		self.assertEqual(a == b, b == a)
		
		b = canopen.objectdictionary.Record("x", 100, 0x00)
		self.assertFalse(a == b)
		self.assertEqual(a == b, b == a)
		
		b = canopen.objectdictionary.Record("rec", 101, 0x00)
		self.assertFalse(a == b)
		self.assertEqual(a == b, b == a)
		
		b = canopen.objectdictionary.Record("rec", 100, 0x01)
		self.assertFalse(a == b)
		self.assertEqual(a == b, b == a)
		
		#### Test step: Contents
		b = canopen.objectdictionary.Record("rec", 100, 0x00)
		b.add(canopen.objectdictionary.Variable("var", 100, 0, canopen.objectdictionary.UNSIGNED32))
		self.assertFalse(a == b)
		
		a.add(canopen.objectdictionary.Variable("var", 100, 0, canopen.objectdictionary.UNSIGNED32))
		self.assertTrue(a == b)
		
		b = canopen.objectdictionary.Record("rec", 100, 0x00)
		b.add(canopen.objectdictionary.Variable("x", 100, 0, canopen.objectdictionary.UNSIGNED32))
		self.assertFalse(a == b)
	
	def test_collection(self):
		record = canopen.objectdictionary.Record("rec", 100, 0x00)
		
		# add
		x = canopen.objectdictionary.Array("arr", 200, canopen.objectdictionary.UNSIGNED32)
		with self.assertRaises(TypeError):
			record.add(x)
		
		x = canopen.objectdictionary.Record("rec", 300, 0x00)
		with self.assertRaises(TypeError):
			record.add(x)
		
		x = canopen.objectdictionary.Variable("var", 200, 0, canopen.objectdictionary.UNSIGNED32)
		with self.assertRaises(ValueError):
			record.add(x)
		
		v1 = canopen.objectdictionary.Variable("var1", 100, 0, canopen.objectdictionary.UNSIGNED32)
		record.add(v1)
		self.assertEqual(len(record), 1)
		
		x = canopen.objectdictionary.Variable("var1", 100, 1, canopen.objectdictionary.UNSIGNED32)
		with self.assertRaises(ValueError):
			record.add(x)
		x = canopen.objectdictionary.Variable("rec", 100, 0, canopen.objectdictionary.UNSIGNED32)
		with self.assertRaises(ValueError):
			record.add(x)
		
		v2 = canopen.objectdictionary.Variable("var2", 100, 1, canopen.objectdictionary.UNSIGNED32)
		record.add(v2)
		self.assertEqual(len(record), 2)
		
		# contains
		self.assertFalse("xxx" in record)
		self.assertFalse(999 in record)
		self.assertTrue(v1.name in record)
		self.assertTrue(v1.subindex in record)
		self.assertTrue(v2.name in record)
		self.assertTrue(v2.subindex in record)
		
		# getitem
		item = record["var1"]
		self.assertTrue(item.name in record)
		
		# iter
		items = []
		for k in record:
			items.append(k)
		
		# delitem
		for x in items:
			del record[x.name]
		
		self.assertEqual(len(record), 0)


if __name__ == "__main__":
	unittest.main()
