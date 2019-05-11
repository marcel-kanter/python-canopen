import unittest
import canopen


class ObjectDictionaryTestCase(unittest.TestCase):
	def test_init(self):
		dictionary = canopen.ObjectDictionary()
	
	def test_collection(self):
		dictionary = canopen.ObjectDictionary()
		
		# append
		x = canopen.ObjectDictionary()
		with self.assertRaises(TypeError):
			dictionary.append(x)
		
		a = canopen.objectdictionary.Array("arr", 100)
		dictionary.append(a)
		self.assertEqual(len(dictionary), 1)
		
		x = canopen.objectdictionary.Array("arr", 200)
		with self.assertRaises(ValueError):
			dictionary.append(x)
		x = canopen.objectdictionary.Record("rec", 100)
		with self.assertRaises(ValueError):
			dictionary.append(x)
		
		r = canopen.objectdictionary.Record("rec", 200)
		dictionary.append(r)
		self.assertEqual(len(dictionary), 2)
		
		v = canopen.objectdictionary.Variable("var", 300, 0)
		dictionary.append(v)
		self.assertEqual(len(dictionary), 3)
		
		# contains
		self.assertFalse("xxx" in dictionary)
		self.assertFalse(999 in dictionary)
		self.assertTrue(a.name in dictionary)
		self.assertTrue(a.index in dictionary)
		self.assertTrue(r.name in dictionary)
		self.assertTrue(r.index in dictionary)
		self.assertTrue(v.name in dictionary)
		self.assertTrue(v.index in dictionary)
		
		# iter, getitem
		items = []
		for k in dictionary:
			items.append(dictionary[k])
		
		# delitem
		for x in items:
			del dictionary[x.name]
		
		self.assertEqual(len(dictionary), 0)


class ArrayTestCase(unittest.TestCase):
	def test_init(self):
		with self.assertRaises(ValueError):
			array = canopen.objectdictionary.Array("arr", -1)
		with self.assertRaises(ValueError):
			array = canopen.objectdictionary.Array("arr", 65536)
		
		name = "arr"
		index = 100
		array = canopen.objectdictionary.Array(name, index)
		
		self.assertEqual(array.name, name)
		self.assertEqual(array.index, index)
		
		with self.assertRaises(AttributeError):
			array.name = name
		with self.assertRaises(AttributeError):
			array.index = index
	
	def test_collection(self):
		array = canopen.objectdictionary.Array("arr", 100)
		
		# append
		x = canopen.objectdictionary.Array("arr", 200)
		with self.assertRaises(TypeError):
			array.append(x)
		
		x = canopen.objectdictionary.Record("rec", 300)
		with self.assertRaises(TypeError):
			array.append(x)
		
		x = canopen.objectdictionary.Variable("var", 200, 0)
		with self.assertRaises(ValueError):
			array.append(x)
		
		v1 = canopen.objectdictionary.Variable("var1", 100, 0)
		array.append(v1)
		self.assertEqual(len(array), 1)
		
		x = canopen.objectdictionary.Variable("var1", 100, 1)
		with self.assertRaises(ValueError):
			array.append(x)
		x = canopen.objectdictionary.Variable("rec", 100, 0)
		with self.assertRaises(ValueError):
			array.append(x)
		
		v2 = canopen.objectdictionary.Variable("var2", 100, 1)
		array.append(v2)
		self.assertEqual(len(array), 2)
		
		# contains
		self.assertFalse("xxx" in array)
		self.assertFalse(999 in array)
		self.assertTrue(v1.name in array)
		self.assertTrue(v1.subindex in array)
		self.assertTrue(v2.name in array)
		self.assertTrue(v2.subindex in array)
		
		# iter, getitem
		items = []
		for k in array:
			items.append(array[k])
		
		# delitem
		for x in items:
			del array[x.name]
		
		self.assertEqual(len(array), 0)


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


class VariableTestCase(unittest.TestCase):
	def test_init(self):
		with self.assertRaises(ValueError):
			variable = canopen.objectdictionary.Variable("var", -1, 0)
		with self.assertRaises(ValueError):
			variable = canopen.objectdictionary.Variable("var", 65536, 0)
		with self.assertRaises(ValueError):
			variable = canopen.objectdictionary.Variable("var", 0, -1)
		with self.assertRaises(ValueError):
			variable = canopen.objectdictionary.Variable("var", 0, 256)
		
		name = "var"
		index = 100
		subindex = 0
		variable = canopen.objectdictionary.Variable(name, index, subindex)
		
		self.assertEqual(variable.name, name)
		self.assertEqual(variable.index, index)
		self.assertEqual(variable.subindex, subindex)
		
		with self.assertRaises(AttributeError):
			variable.name = name
		with self.assertRaises(AttributeError):
			variable.index = index
		with self.assertRaises(AttributeError):
			variable.subindex = subindex


if __name__ == "__main__":
	unittest.main()
