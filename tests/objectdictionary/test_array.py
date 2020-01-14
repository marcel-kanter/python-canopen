import unittest
from hypothesis import given, example, settings
import hypothesis.strategies as st

from canopen.objectdictionary import Array, DefType, Domain, Record, Variable
from canopen.objectdictionary.datatypes import UNSIGNED8, UNSIGNED16, UNSIGNED32


class ArrayTestCase(unittest.TestCase):
	@given(
		name = st.text(),
		index = st.integers(),
		data_type = st.integers(),
		description = st.text()
	)
	@settings(max_examples = 1000)
	@example(name = "arr", index = -1, data_type = 0, description = "", valid_example = False)
	@example(name = "arr", index = 65536, data_type = 0, description = "", valid_example = False)
	@example(name = "arr", index = 0, data_type = -1, description = "", valid_example = False)
	@example(name = "arr", index = 0, data_type = 65536, description = "", valid_example = False)
	def test_init(self, **kwargs):
		name = kwargs["name"]
		index = kwargs["index"]
		data_type = kwargs["data_type"]
		description = kwargs["description"]
		
		valid_example = (
			len(name) >= 0
			and index >= 0x0000 and index <= 0xFFFF
			and data_type >= 0x0000 and data_type <= 0x1000
		)
		
		if "valid_example" in kwargs:
			self.assertEqual(valid_example, kwargs["valid_example"])
			del kwargs["valid_example"]
		
		if valid_example:
			examinee = Array(**kwargs)
			examinee.description = description
			
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
		
			description = "Franz jagt im komplett verwahrlosten Taxi quer durch Bayern."
			examinee.description = description
			self.assertEqual(examinee.description, description)
		else:
			with self.assertRaises(ValueError):
				Array(**kwargs)
	
	def test_equals(self):
		a = Array("arr", 100, UNSIGNED32)
		
		#### Test step: Reflexivity
		self.assertTrue(a == a)
		
		#### Test step: Compare same classes only (required for transitivity)
		test_data = [None, 3]
		for value in test_data:
			with self.subTest("value=" + str(value)):
				self.assertFalse(a == value)
		
		#### Test step: Consistency
		b = Array("arr", 100, UNSIGNED32)
		for _ in range(3):
			self.assertTrue(a == b)
		
		#### Test step: Symmetricality, Contents
		b = Array("arr", 100, UNSIGNED32)
		self.assertTrue(a == b)
		self.assertEqual(a == b, b == a)
		
		b = Array("x", 100, UNSIGNED32)
		self.assertFalse(a == b)
		self.assertEqual(a == b, b == a)
		
		b = Array("arr", 101, UNSIGNED32)
		self.assertFalse(a == b)
		self.assertEqual(a == b, b == a)
		
		b = Array("arr", 100, UNSIGNED16)
		self.assertFalse(a == b)
		self.assertEqual(a == b, b == a)
		
		b = Array("arr", 100, UNSIGNED32)
		b.description = a.description + "XXX"
		self.assertFalse(a == b)
		self.assertEqual(a == b, b == a)
		
		#### Test step: Contents
		b = Array("arr", 100, UNSIGNED32)
		b.add(Variable("var", 100, 0, UNSIGNED8))
		self.assertFalse(a == b)
		
		a.add(Variable("var", 100, 0, UNSIGNED8))
		self.assertTrue(a == b)
		
		b = Array("arr", 100, UNSIGNED32)
		b.add(Variable("x", 100, 0, UNSIGNED8))
		self.assertFalse(a == b)
	
	def test_collection(self):
		array = Array("arr", 100, UNSIGNED32)
		
		# add
		x = Array("arr", 200, UNSIGNED32)
		with self.assertRaises(TypeError):
			array.add(x)
		
		x = Record("rec", 100, 0x00)
		with self.assertRaises(TypeError):
			array.add(x)
		
		x = Domain("domain", 100)
		with self.assertRaises(TypeError):
			array.add(x)
		
		x = DefType("deftype", 100)
		with self.assertRaises(TypeError):
			array.add(x)
		
		x = Variable("var", 200, 0, UNSIGNED32)
		with self.assertRaises(ValueError):
			array.add(x)
		
		v1 = Variable("var1", 100, 0, UNSIGNED8)
		array.add(v1)
		self.assertEqual(len(array), 1)
		
		x = Variable("var1", 100, 1, UNSIGNED32)
		with self.assertRaises(ValueError):
			array.add(x)
		x = Variable("rec", 100, 0, UNSIGNED32)
		with self.assertRaises(ValueError):
			array.add(x)
		
		v2 = Variable("var2", 100, 1, UNSIGNED32)
		array.add(v2)
		self.assertEqual(len(array), 2)
		
		v3 = Variable("var3", 100, 0xFF, UNSIGNED32)
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
