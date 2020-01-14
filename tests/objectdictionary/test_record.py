import unittest
from hypothesis import given, example, settings
import hypothesis.strategies as st

from canopen.objectdictionary import Array, DefStruct, Record, Variable 
from canopen.objectdictionary.datatypes import UNSIGNED32


class RecordTestCase(unittest.TestCase):
	@given(
		name = st.text(),
		index = st.integers(),
		data_type = st.integers(),
		description = st.text()
	)
	@settings(max_examples = 1000)
	@example(name = "rec", index = -1, data_type = 0, description = "", valid_example = False)
	@example(name = "rec", index = 65536, data_type = 0, description = "", valid_example = False)
	@example(name = "rec", index = 0, data_type = -1, description = "", valid_example = False)
	@example(name = "rec", index = 0, data_type = 65536, description = "", valid_example = False)
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
			examinee = Record(**kwargs)
			examinee.description = description
			
			self.assertEqual(examinee.object_type, 9)
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
				Record(**kwargs)
	
	def test_equals(self):
		a = Record("rec", 100, 0x00)
		
		#### Test step: Reflexivity
		self.assertTrue(a == a)
		
		#### Test step: Compare same classes only (required for transitivity)
		test_data = [None, 3, DefStruct("rec", 100)]
		for value in test_data:
			with self.subTest("value=" + str(value)):
				self.assertFalse(a == value)
		
		#### Test step: Consistency
		b = Record("rec", 100, 0x00)
		for _ in range(3):
			self.assertTrue(a == b)
		
		#### Test step: Symmetricality, Contents
		b = Record("rec", 100, 0x00)
		self.assertTrue(a == b)
		self.assertEqual(a == b, b == a)
		
		b = Record("x", 100, 0x00)
		self.assertFalse(a == b)
		self.assertEqual(a == b, b == a)
		
		b = Record("rec", 101, 0x00)
		self.assertFalse(a == b)
		self.assertEqual(a == b, b == a)
		
		b = Record("rec", 100, 0x01)
		self.assertFalse(a == b)
		self.assertEqual(a == b, b == a)
		
		b = Record("rec", 100, 0x00)
		b.description = a.description + "XXX"
		self.assertFalse(a == b)
		self.assertEqual(a == b, b == a)
		
		#### Test step: Contents
		b = Record("rec", 100, 0x00)
		b.add(Variable("var", 100, 0, UNSIGNED32))
		self.assertFalse(a == b)
		
		a.add(Variable("var", 100, 0, UNSIGNED32))
		self.assertTrue(a == b)
		
		b = Record("rec", 100, 0x00)
		b.add(Variable("x", 100, 0, UNSIGNED32))
		self.assertFalse(a == b)
	
	def test_collection(self):
		record = Record("rec", 100, 0x00)
		
		# add
		x = Array("arr", 200, UNSIGNED32)
		with self.assertRaises(TypeError):
			record.add(x)
		
		x = Record("rec", 300, 0x00)
		with self.assertRaises(TypeError):
			record.add(x)
		
		x = Variable("var", 200, 0, UNSIGNED32)
		with self.assertRaises(ValueError):
			record.add(x)
		
		v1 = Variable("var1", 100, 0, UNSIGNED32)
		record.add(v1)
		self.assertEqual(len(record), 1)
		
		x = Variable("var1", 100, 1, UNSIGNED32)
		with self.assertRaises(ValueError):
			record.add(x)
		x = Variable("rec", 100, 0, UNSIGNED32)
		with self.assertRaises(ValueError):
			record.add(x)
		
		v2 = Variable("var2", 100, 1, UNSIGNED32)
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
