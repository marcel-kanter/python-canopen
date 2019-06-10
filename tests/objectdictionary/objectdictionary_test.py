import unittest
import canopen.objectdictionary


class ObjectDictionaryTestCase(unittest.TestCase):
	def test_init(self):
		canopen.ObjectDictionary()
	
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
		
		ds = canopen.objectdictionary.DefStruct("defstruct", 0x40)
		dictionary.append(ds)
		self.assertEqual(len(dictionary), 2)
		
		with self.assertRaises(ValueError):
			dictionary.append(ds)
		
		dt = canopen.objectdictionary.DefStruct("deftype", 0x60)
		dictionary.append(dt)
		self.assertEqual(len(dictionary), 3)
		
		with self.assertRaises(ValueError):
			dictionary.append(dt)
		
		r = canopen.objectdictionary.Record("rec", 200)
		dictionary.append(r)
		self.assertEqual(len(dictionary), 4)
		
		with self.assertRaises(ValueError):
			dictionary.append(r)
		
		v = canopen.objectdictionary.Variable("var", 300, 0, canopen.objectdictionary.UNSIGNED32)
		dictionary.append(v)
		self.assertEqual(len(dictionary), 5)
		
		with self.assertRaises(ValueError):
			dictionary.append(v)
		
		# contains
		self.assertFalse("xxx" in dictionary)
		self.assertFalse(99 in dictionary)
		self.assertTrue(a.name in dictionary)
		self.assertTrue(a.index in dictionary)
		self.assertTrue(ds.name in dictionary)
		self.assertTrue(ds.index in dictionary)
		self.assertTrue(dt.name in dictionary)
		self.assertTrue(dt.index in dictionary)
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


if __name__ == "__main__":
	unittest.main()
