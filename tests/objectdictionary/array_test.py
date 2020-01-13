import unittest
import canopen.objectdictionary


class ArrayTestCase(unittest.TestCase):
	def test_init(self):
		with self.assertRaises(ValueError):
			canopen.objectdictionary.Array("arr", -1, canopen.objectdictionary.UNSIGNED32)
		with self.assertRaises(ValueError):
			canopen.objectdictionary.Array("arr", 65536, canopen.objectdictionary.UNSIGNED32)
		with self.assertRaises(ValueError):
			canopen.objectdictionary.Array("arr", 0, -1)
		with self.assertRaises(ValueError):
			canopen.objectdictionary.Array("arr", 0, 65536)
		
		name = "arr"
		index = 100
		data_type = canopen.objectdictionary.UNSIGNED32
		description = "abc"
		examinee = canopen.objectdictionary.Array(name, index, data_type, description)
		
		self.assertEqual(examinee.object_type, 8)
		self.assertEqual(examinee.name, name)
		self.assertEqual(examinee.index, index)
		self.assertEqual(examinee.data_type, data_type)
		self.assertEqual(examinee.description, description)
		
		with self.assertRaises(AttributeError):
			examinee.name = name
		with self.assertRaises(AttributeError):
			examinee.index = index
		with self.assertRaises(AttributeError):
			examinee.data_type = data_type
		
		desc = "Franz jagt im komplett verwahrlosten Taxi quer durch Bayern."
		examinee.description = desc
		self.assertEqual(examinee.description, desc)
	
	def test_equals(self):
		a = canopen.objectdictionary.Array("arr", 100, canopen.objectdictionary.UNSIGNED32)
		
		#### Test step: Reflexivity
		self.assertTrue(a == a)
		
		#### Test step: Compare same classes only (required for transitivity)
		test_data = [None, 3]
		for value in test_data:
			with self.subTest("value=" + str(value)):
				self.assertFalse(a == value)
		
		#### Test step: Consistency
		b = canopen.objectdictionary.Array("arr", 100, canopen.objectdictionary.UNSIGNED32)
		for _ in range(3):
			self.assertTrue(a == b)
		
		#### Test step: Symmetricality, Contents
		b = canopen.objectdictionary.Array("arr", 100, canopen.objectdictionary.UNSIGNED32)
		self.assertTrue(a == b)
		self.assertEqual(a == b, b == a)
		
		b = canopen.objectdictionary.Array("x", 100, canopen.objectdictionary.UNSIGNED32)
		self.assertFalse(a == b)
		self.assertEqual(a == b, b == a)
		
		b = canopen.objectdictionary.Array("arr", 101, canopen.objectdictionary.UNSIGNED32)
		self.assertFalse(a == b)
		self.assertEqual(a == b, b == a)
		
		b = canopen.objectdictionary.Array("arr", 100, canopen.objectdictionary.UNSIGNED16)
		self.assertFalse(a == b)
		self.assertEqual(a == b, b == a)
		
		b = canopen.objectdictionary.Array("arr", 100, canopen.objectdictionary.UNSIGNED32)
		b.description = a.description + "XXX"
		self.assertFalse(a == b)
		self.assertEqual(a == b, b == a)
		
		#### Test step: Contents
		b = canopen.objectdictionary.Array("arr", 100, canopen.objectdictionary.UNSIGNED32)
		b.add(canopen.objectdictionary.Variable("var", 100, 0, canopen.objectdictionary.UNSIGNED8))
		self.assertFalse(a == b)
		
		a.add(canopen.objectdictionary.Variable("var", 100, 0, canopen.objectdictionary.UNSIGNED8))
		self.assertTrue(a == b)
		
		b = canopen.objectdictionary.Array("arr", 100, canopen.objectdictionary.UNSIGNED32)
		b.add(canopen.objectdictionary.Variable("x", 100, 0, canopen.objectdictionary.UNSIGNED8))
		self.assertFalse(a == b)
	
	def test_collection(self):
		array = canopen.objectdictionary.Array("arr", 100, canopen.objectdictionary.UNSIGNED32)
		
		# add
		x = canopen.objectdictionary.Array("arr", 200, canopen.objectdictionary.UNSIGNED32)
		with self.assertRaises(TypeError):
			array.add(x)
		
		x = canopen.objectdictionary.Record("rec", 100, 0x00)
		with self.assertRaises(TypeError):
			array.add(x)
		
		x = canopen.objectdictionary.Domain("domain", 100)
		with self.assertRaises(TypeError):
			array.add(x)
		
		x = canopen.objectdictionary.DefType("deftype", 100)
		with self.assertRaises(TypeError):
			array.add(x)
		
		x = canopen.objectdictionary.Variable("var", 200, 0, canopen.objectdictionary.UNSIGNED32)
		with self.assertRaises(ValueError):
			array.add(x)
		
		v1 = canopen.objectdictionary.Variable("var1", 100, 0, canopen.objectdictionary.UNSIGNED8)
		array.add(v1)
		self.assertEqual(len(array), 1)
		
		x = canopen.objectdictionary.Variable("var1", 100, 1, canopen.objectdictionary.UNSIGNED32)
		with self.assertRaises(ValueError):
			array.add(x)
		x = canopen.objectdictionary.Variable("rec", 100, 0, canopen.objectdictionary.UNSIGNED32)
		with self.assertRaises(ValueError):
			array.add(x)
		
		v2 = canopen.objectdictionary.Variable("var2", 100, 1, canopen.objectdictionary.UNSIGNED32)
		array.add(v2)
		self.assertEqual(len(array), 2)
		
		v3 = canopen.objectdictionary.Variable("var3", 100, 0xFF, canopen.objectdictionary.UNSIGNED32)
		array.add(v3)
		self.assertEqual(len(array), 3)
		
		# contains
		self.assertFalse("xxx" in array)
		self.assertFalse(999 in array)
		self.assertTrue(v1.name in array)
		self.assertTrue(v1.subindex in array)
		self.assertTrue(v2.name in array)
		self.assertTrue(v2.subindex in array)
		self.assertTrue(v3.name in array)
		self.assertTrue(v3.subindex in array)
		
		# getitem
		item = array["var1"]
		self.assertTrue(item.name in array)
		
		# iter
		items = []
		for k in array:
			items.append(k)
		
		# delitem
		for x in items:
			del array[x.name]
		
		self.assertEqual(len(array), 0)


if __name__ == "__main__":
	unittest.main()
