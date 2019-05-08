import unittest
import canopen


class ObjectDictionaryTestCase(unittest.TestCase):
	def test_init(self):
		dictionary = canopen.ObjectDictionary()


class ArrayTestCase(unittest.TestCase):
	def test_init(self):
		with self.assertRaises(ValueError):
			array = canopen.objectdictionary.Array('arr', -1)
		with self.assertRaises(ValueError):
			array = canopen.objectdictionary.Array('arr', 65536)
		
		name = 'arr'
		index = 100
		array = canopen.objectdictionary.Array(name, index)
		
		self.assertEqual(array.name, name)
		self.assertEqual(array.index, index)
		
		with self.assertRaises(AttributeError):
			array.name = name
		with self.assertRaises(AttributeError):
			array.index = index


class RecordTestCase(unittest.TestCase):
	def test_init(self):
		with self.assertRaises(ValueError):
			record = canopen.objectdictionary.Record('rec', -1)
		with self.assertRaises(ValueError):
			record = canopen.objectdictionary.Record('rec', 65536)
		
		name = 'rec'
		index = 100
		record = canopen.objectdictionary.Record(name, index)
		
		self.assertEqual(record.name, name)
		self.assertEqual(record.index, index)
		
		with self.assertRaises(AttributeError):
			record.name = name
		with self.assertRaises(AttributeError):
			record.index = index


class VariableTestCase(unittest.TestCase):
	def test_init(self):
		with self.assertRaises(ValueError):
			variable = canopen.objectdictionary.Variable('var', -1, 0)
		with self.assertRaises(ValueError):
			variable = canopen.objectdictionary.Variable('var', 65536, 0)
		with self.assertRaises(ValueError):
			variable = canopen.objectdictionary.Variable('var', 0, -1)
		with self.assertRaises(ValueError):
			variable = canopen.objectdictionary.Variable('var', 0, 256)
		
		name = 'var'
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
