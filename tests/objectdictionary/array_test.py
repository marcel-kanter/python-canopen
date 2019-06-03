import unittest
import canopen.objectdictionary


class ArrayTestCase(unittest.TestCase):
	def test_init(self):
		with self.assertRaises(ValueError):
			canopen.objectdictionary.Array("arr", -1)
		with self.assertRaises(ValueError):
			canopen.objectdictionary.Array("arr", 65536)
		
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
		
		x = canopen.objectdictionary.Variable("var", 200, 0, canopen.objectdictionary.UNSIGNED32)
		with self.assertRaises(ValueError):
			array.append(x)
		
		v1 = canopen.objectdictionary.Variable("var1", 100, 0, canopen.objectdictionary.UNSIGNED32)
		array.append(v1)
		self.assertEqual(len(array), 1)
		
		x = canopen.objectdictionary.Variable("var1", 100, 1, canopen.objectdictionary.UNSIGNED32)
		with self.assertRaises(ValueError):
			array.append(x)
		x = canopen.objectdictionary.Variable("rec", 100, 0, canopen.objectdictionary.UNSIGNED32)
		with self.assertRaises(ValueError):
			array.append(x)
		
		v2 = canopen.objectdictionary.Variable("var2", 100, 1, canopen.objectdictionary.UNSIGNED32)
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


if __name__ == "__main__":
	unittest.main()
