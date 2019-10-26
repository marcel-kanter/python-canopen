import unittest
import canopen.objectdictionary


class ObjectDictionaryTestCase(unittest.TestCase):
	def test_init(self):
		canopen.ObjectDictionary()
	
	def test_equals(self):
		a = canopen.objectdictionary.ObjectDictionary()
		
		#### Test step: Reflexivity
		self.assertTrue(a == a)
		
		#### Test step: Compare same classes only (required for transitivity)
		test_data = [None, 3]
		for value in test_data:
			with self.subTest("value=" + str(value)):
				self.assertFalse(a == value)
		
		#### Test step: Consistency
		b = canopen.objectdictionary.ObjectDictionary()
		for _ in range(3):
			self.assertTrue(a == b)
		
		#### Test step: Symmetricality, Contents
		b = canopen.objectdictionary.ObjectDictionary()
		self.assertTrue(a == b)
		self.assertEqual(a == b, b == a)
		
		b.add(canopen.objectdictionary.Variable("var", 100, 0, canopen.objectdictionary.UNSIGNED32))
		self.assertFalse(a == b)
		self.assertEqual(a == b, b == a)
		
		a.add(canopen.objectdictionary.Variable("var", 100, 0, canopen.objectdictionary.UNSIGNED32))
		self.assertTrue(a == b)
		self.assertEqual(a == b, b == a)
		
		a.add(canopen.objectdictionary.Record("rec", 200))
		b.add(canopen.objectdictionary.Record("rec", 200))
		self.assertTrue(a == b)
		self.assertEqual(a == b, b == a)
		
		b["rec"].add(canopen.objectdictionary.Variable("var", 200, 0, canopen.objectdictionary.UNSIGNED32))
		self.assertFalse(a == b)
		self.assertEqual(a == b, b == a)
		
		a["rec"].add(canopen.objectdictionary.Variable("var", 200, 0, canopen.objectdictionary.UNSIGNED32))
		self.assertTrue(a == b)
		self.assertEqual(a == b, b == a)
		
		b = canopen.objectdictionary.ObjectDictionary()
		b.add(canopen.objectdictionary.Variable("x", 100, 0, canopen.objectdictionary.UNSIGNED32))
		self.assertFalse(a == b)
		self.assertEqual(a == b, b == a)
			
	def test_collection(self):
		dictionary = canopen.ObjectDictionary()
		
		# add
		x = canopen.ObjectDictionary()
		with self.assertRaises(TypeError):
			dictionary.add(x)
		
		a = canopen.objectdictionary.Array("arr", 100)
		dictionary.add(a)
		self.assertEqual(len(dictionary), 1)
		
		x = canopen.objectdictionary.Array("arr", 200)
		with self.assertRaises(ValueError):
			dictionary.add(x)
		x = canopen.objectdictionary.Record("rec", 100)
		with self.assertRaises(ValueError):
			dictionary.add(x)
		
		ds = canopen.objectdictionary.DefStruct("defstruct", 0x40)
		dictionary.add(ds)
		self.assertEqual(len(dictionary), 2)
		
		with self.assertRaises(ValueError):
			dictionary.add(ds)
		
		dt = canopen.objectdictionary.DefStruct("deftype", 0x60)
		dictionary.add(dt)
		self.assertEqual(len(dictionary), 3)
		
		with self.assertRaises(ValueError):
			dictionary.add(dt)
		
		r = canopen.objectdictionary.Record("rec", 200)
		dictionary.add(r)
		self.assertEqual(len(dictionary), 4)
		
		with self.assertRaises(ValueError):
			dictionary.add(r)
		
		v = canopen.objectdictionary.Variable("var", 300, 0, canopen.objectdictionary.UNSIGNED32)
		dictionary.add(v)
		self.assertEqual(len(dictionary), 5)
		
		with self.assertRaises(ValueError):
			dictionary.add(v)
		
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
		
		# getitem
		item = dictionary["var"]
		self.assertTrue(item.name in dictionary)
		
		# iter
		items = []
		for k in dictionary:
			items.append(k)
		
		# delitem
		for x in items:
			del dictionary[x.name]
		
		self.assertEqual(len(dictionary), 0)


if __name__ == "__main__":
	unittest.main()
