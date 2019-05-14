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


if __name__ == "__main__":
	unittest.main()
