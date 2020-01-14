import unittest
import struct
import calendar
from hypothesis import given, example, settings
import hypothesis.strategies as st

from canopen.objectdictionary import Variable, DefType
from canopen.objectdictionary.datatypes import *


class VariableTestCase(unittest.TestCase):
	@given(
		name = st.text(),
		index = st.integers(),
		subindex = st.integers(),
		data_type = st.integers(),
		access_type = st.text(),
		description = st.text()
	)
	@settings(max_examples = 1000)
	@example(name = "var", index = 0x1000, subindex = 0x00, data_type = UNSIGNED32, access_type = "rw", description = "", valid_example = True)
	@example(name = "var", index = -1, subindex = 0, data_type = UNSIGNED32, access_type = "rw", description = "", valid_example = False)
	@example(name = "var", index = 65536, subindex = 0, data_type = UNSIGNED32, access_type = "rw", description = "", valid_example = False)
	@example(name = "var", index = 0, subindex = -1, data_type = UNSIGNED32, access_type = "rw", description = "", valid_example = False)
	@example(name = "var", index = 0, subindex = 256, data_type = UNSIGNED32, access_type = "rw", description = "", valid_example = False)
	@example(name = "var", index = 0, subindex = 0, data_type = 0, access_type = "rw", description = "", valid_example = False)
	@example(name = "var", index = 0, subindex = 0, data_type = UNSIGNED32, access_type = "X", description = "", valid_example = False)
	def test_init(self, **kwargs):
		name = kwargs["name"]
		index = kwargs["index"]
		subindex = kwargs["subindex"]
		data_type = kwargs["data_type"]
		access_type = kwargs["access_type"]
		description = kwargs["description"]
		
		valid_example = (
			len(name) >= 0
			and index >= 0x0000 and index <= 0xFFFF
			and subindex >= 0x00 and subindex <= 0xFF
			and data_type in [BOOLEAN, INTEGER8, INTEGER16, INTEGER32, UNSIGNED8, UNSIGNED16, UNSIGNED32, REAL32, VISIBLE_STRING, OCTET_STRING, UNICODE_STRING, TIME_OF_DAY, TIME_DIFFERENCE, DOMAIN, INTEGER24, REAL64, INTEGER40, INTEGER48, INTEGER56, INTEGER64, UNSIGNED24, UNSIGNED40, UNSIGNED48, UNSIGNED56, UNSIGNED64]
			and access_type in ["ro", "wo", "rw", "const"]
		)
		
		if "valid_example" in kwargs:
			self.assertEqual(valid_example, kwargs["valid_example"])
			del kwargs["valid_example"]
		
		if valid_example:
			examinee = Variable(**kwargs)
			examinee.description = description
			
			self.assertEqual(examinee.object_type, 7)
			self.assertEqual(examinee.name, name)
			self.assertEqual(examinee.index, index)
			self.assertEqual(examinee.subindex, subindex)
			self.assertEqual(examinee.data_type, data_type)
			self.assertEqual(examinee.access_type, access_type)
			self.assertEqual(examinee.description, description)
			
			with self.assertRaises(AttributeError):
				examinee.name = name
			with self.assertRaises(AttributeError):
				examinee.index = index
			with self.assertRaises(AttributeError):
				examinee.subindex = subindex
			with self.assertRaises(AttributeError):
				examinee.data_type = data_type
			
			with self.assertRaises(ValueError):
				examinee.access_type = "xx"
			
			for access_type in ["rw", "wo", "ro", "const"]:
				examinee.access_type = access_type
				self.assertEqual(examinee.access_type, access_type)
			
			self.assertEqual(examinee.default_value, examinee.decode(examinee.encode(examinee.default_value)))
			
			examinee.default_value = 100
			self.assertEqual(examinee.default_value, 100)
			
			description = "Franz jagt im komplett verwahrlosten Taxi quer durch Bayern."
			examinee.description = description
			self.assertEqual(examinee.description, description)
		else:
			with self.assertRaises(ValueError):
				Variable(**kwargs)
	
	def test_equals(self):
		a = Variable("var", 100, 0, UNSIGNED32, "rw")
		
		#### Test step: Reflexivity
		self.assertTrue(a == a)
		
		#### Test step: Compare same classes only (required for transitivity)
		test_data = [None, 3, DefType("var", 100)]
		for value in test_data:
			with self.subTest("value=" + str(value)):
				self.assertFalse(a == value)
		
		#### Test step: Consistency
		b = Variable("var", 100, 0, UNSIGNED32, "rw")
		for _ in range(3):
			self.assertTrue(a == b)
		
		#### Test step: Symmetricality, Contents
		b = Variable("var", 100, 0, UNSIGNED32, "rw")
		self.assertTrue(a == b)
		self.assertEqual(a == b, b == a)
		
		b = Variable("x", 100, 0, UNSIGNED32, "rw")
		self.assertFalse(a == b)
		self.assertEqual(a == b, b == a)
		
		b = Variable("var", 111, 0, UNSIGNED32, "rw")
		self.assertFalse(a == b)
		self.assertEqual(a == b, b == a)
		
		b = Variable("var", 100, 1, UNSIGNED32, "rw")
		self.assertFalse(a == b)
		self.assertEqual(a == b, b == a)
		
		b = Variable("var", 100, 0, BOOLEAN, "rw")
		self.assertFalse(a == b)
		self.assertEqual(a == b, b == a)
		
		b = Variable("var", 100, 0, UNSIGNED32, "ro")
		self.assertFalse(a == b)
		self.assertEqual(a == b, b == a)
		
		b = Variable("var", 100, 0, UNSIGNED32, "rw")
		b.default_value = 10
		self.assertFalse(a == b)
		self.assertEqual(a == b, b == a)
		
		b = Variable("var", 100, 0, UNSIGNED32, "rw")
		b.description = a.description + "XXX"
		self.assertFalse(a == b)
		self.assertEqual(a == b, b == a)
	
	def test_boolean(self):
		variable = Variable("BOOLEAN", 100, 0, BOOLEAN)
		
		self.assertEqual(variable.size, 1)
		
		with self.subTest("encode"):
			test_data = [(False, b"\x00"),
				(True, b"\x01")]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.encode(x), y)
		
		with self.subTest("decode"):
			test_data = [(b"\x00", False),
				(b"\x01", True),
				(b"\x01\x00", True),
				(b"\x00\x00", False)]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.decode(x), y)
	
	def test_integer8(self):
		variable = Variable("INTEGER8", 100, 0, INTEGER8)
		
		self.assertEqual(variable.size, 8)
		
		with self.subTest("encode"):
			test_data = [(0, b"\x00"),
				(1, b"\x01")]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.encode(x), y)
			
			test_data = [-2 ** 7 - 1, 2 ** 7]
			for x in test_data:
				with self.subTest("x=" + str(x)):
					with self.assertRaises(ValueError):
						variable.encode(x)
		
		with self.subTest("decode"):
			test_data = [(b"\x00", 0),
				(b"\x55", 85),
				(b"\xAA", -86),
				(b"\x55\xFF", 85),
				(b"\xAA\x00", -86)]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.decode(x), y)
	
	def test_integer16(self):
		variable = Variable("INTEGER16", 100, 0, INTEGER16)
		
		self.assertEqual(variable.size, 16)
		
		with self.subTest("encode"):
			test_data = [(0, b"\x00\x00"),
				(1, b"\x01\x00"),
				(85, b"\x55\x00"),
				(-86, b"\xAA\xFF"),
				(-21931, b"\x55\xAA"),
				(21930, b"\xAA\x55")]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.encode(x), y)
			
			test_data = [-2 ** 15 - 1, 2 ** 15]
			for x in test_data:
				with self.subTest("x=" + str(x)):
					with self.assertRaises(ValueError):
						variable.encode(x)
		
		with self.subTest("decode"):
			test_data = [(b"\x00\x00", 0),
				(b"\x55\xAA", -21931),
				(b"\xAA\x55", 21930),
				(b"\x55\xAA\x00", -21931),
				(b"\xAA\x55\xFF", 21930)]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.decode(x), y)
			
			test_data = [b"\x00"]
			for x in test_data:
				with self.subTest("x=" + str(x)):
					with self.assertRaises(ValueError):
						variable.decode(x)
	
	def test_integer32(self):
		variable = Variable("INTEGER32", 100, 0, INTEGER32)
		
		self.assertEqual(variable.size, 32)
		
		with self.subTest("encode"):
			test_data = [(0, b"\x00\x00\x00\x00"),
				(-1437226411, b"\x55\xAA\x55\xAA"),
				(1437226410, b"\xAA\x55\xAA\x55")]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.encode(x), y)
			
			test_data = [-2 ** 31 - 1, 2 ** 31]
			for x in test_data:
				with self.subTest("x=" + str(x)):
					with self.assertRaises(ValueError):
						variable.encode(x)
		
		with self.subTest("decode"):
			test_data = [(b"\x00\x00\x00\x00", 0),
				(b"\x55\xAA\x55\xAA", -1437226411),
				(b"\xAA\x55\xAA\x55", 1437226410),
				(b"\x55\xAA\x55\xAA\x00", -1437226411),
				(b"\xAA\x55\xAA\x55\xFF", 1437226410)]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.decode(x), y)
			
			test_data = [b"\x00"]
			for x in test_data:
				with self.subTest("x=" + str(x)):
					with self.assertRaises(ValueError):
						variable.decode(x)
	
	def test_unsigned8(self):
		variable = Variable("UNSIGNED8", 100, 0, UNSIGNED8)
		
		self.assertEqual(variable.size, 8)
		
		with self.subTest("encode"):
			test_data = [(0, b"\x00"),
				(85, b"\x55"),
				(170, b"\xAA")]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.encode(x), y)
			
			test_data = [-1, 2 ** 8]
			for x in test_data:
				with self.subTest("x=" + str(x)):
					with self.assertRaises(ValueError):
						variable.encode(x)
		
		with self.subTest("decode"):
			test_data = [(b"\x00", 0),
				(b"\x55", 85),
				(b"\xAA", 170),
				(b"\x55\xFF", 85),
				(b"\xAA\xFF", 170)]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.decode(x), y)
	
	def test_unsigned16(self):
		variable = Variable("UNSIGNED16", 100, 0, UNSIGNED16)
		
		self.assertEqual(variable.size, 16)
		
		with self.subTest("encode"):
			test_data = [(0, b"\x00\x00"),
				(43605, b"\x55\xAA"),
				(21930, b"\xAA\x55")]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.encode(x), y)
			
			test_data = [-1, 2 ** 16]
			for x in test_data:
				with self.subTest("x=" + str(x)):
					with self.assertRaises(ValueError):
						variable.encode(x)
		
		with self.subTest("decode"):
			test_data = [(b"\x00\x00", 0),
				(b"\x55\xAA", 43605),
				(b"\xAA\x55", 21930),
				(b"\x55\xAA\xFF", 43605),
				(b"\xAA\x55\x55", 21930)]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.decode(x), y)
			
			test_data = [b"\x00"]
			for x in test_data:
				with self.subTest("x=" + str(x)):
					with self.assertRaises(ValueError):
						variable.decode(x)
	
	def test_unsigned32(self):
		variable = Variable("UNSIGNED32", 100, 0, UNSIGNED32)
		
		self.assertEqual(variable.size, 32)
		
		with self.subTest("encode"):
			test_data = [(0, b"\x00\x00\x00\x00"),
				(2857740885, b"\x55\xAA\x55\xAA"),
				(1437226410, b"\xAA\x55\xAA\x55")]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.encode(x), y)
			
			test_data = [-1, 2 ** 32]
			for x in test_data:
				with self.subTest("x=" + str(x)):
					with self.assertRaises(ValueError):
						variable.encode(x)
		
		with self.subTest("decode"):
			test_data = [(b"\x00\x00\x00\x00", 0),
				(b"\x55\xAA\x55\xAA", 2857740885),
				(b"\xAA\x55\xAA\x55", 1437226410),
				(b"\x55\xAA\x55\xAA\xFF", 2857740885),
				(b"\xAA\x55\xAA\x55\xFF", 1437226410)]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.decode(x), y)
			
			test_data = [b"\x00"]
			for x in test_data:
				with self.subTest("x=" + str(x)):
					with self.assertRaises(ValueError):
						variable.decode(x)
	
	def test_real32(self):
		variable = Variable("REAL32", 100, 0, REAL32)
		
		self.assertEqual(variable.size, 32)
		
		with self.subTest("encode"):
			test_data = [(0.0, b"\x00\x00\x00\x00")]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.encode(x), y)
		
		with self.subTest("decode"):
			test_data = [(b"\x00\x00\x00\x00", 0.0)]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.decode(x), y)
			
			test_data = [b"\x00"]
			for x in test_data:
				with self.subTest("x=" + str(x)):
					with self.assertRaises(ValueError):
						variable.decode(x)
	
	def test_visible_string(self):
		variable = Variable("VISIBLE_STRING", 100, 0, VISIBLE_STRING)
		
		self.assertEqual(variable.size, 0)
		
		with self.subTest("encode"):
			test_data = [("TEXT", b"TEXT")]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.encode(x), y)
		
		with self.subTest("decode"):
			test_data = [(b"TEXT", "TEXT")]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.decode(x), y)
	
	def test_octet_string(self):
		variable = Variable("OCTET_STRING", 100, 0, OCTET_STRING)
		
		self.assertEqual(variable.size, 0)
		
		with self.subTest("encode"):
			test_data = [("TEXT", b"TEXT")]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.encode(x), y)
		
		with self.subTest("decode"):
			test_data = [(b"TEXT", "TEXT")]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.decode(x), y)
	
	def test_unicode_string(self):
		variable = Variable("UNICODE_STRING", 100, 0, UNICODE_STRING)
		
		self.assertEqual(variable.size, 0)
		
		with self.subTest("encode"):
			test_data = [("TEXT", b"T\x00E\x00X\x00T\x00")]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.encode(x), y)
		
		with self.subTest("decode"):
			test_data = [(b"T\x00E\x00X\x00T\x00", "TEXT")]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.decode(x), y)
	
	def test_time_of_day(self):	
		variable = Variable("TIME_OF_DAY", 100, 0, TIME_OF_DAY)
		
		self.assertEqual(variable.size, 48)
		
		with self.subTest("encode"):
			test_data = [(calendar.timegm((1984, 1, 1, 0, 0, 0)), struct.pack("<LH", 0, 0))]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.encode(x), y)
			
			with self.assertRaises(ValueError):
				variable.encode(0)
		
		with self.subTest("decode"):
			test_data = [(struct.pack("<LH", 0, 0), calendar.timegm((1984, 1, 1, 0, 0, 0))),
				(struct.pack("<LH", 10 * 60 * 60 * 1000, 0), calendar.timegm((1984, 1, 1, 10, 0, 0))),
				(struct.pack("<LH", 0, 366), calendar.timegm((1985, 1, 1, 0, 0, 0)))]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.decode(x), y)
	
	def test_time_difference(self):
		variable = Variable("TIME_DIFFERENCE", 100, 0, TIME_DIFFERENCE)
		
		self.assertEqual(variable.size, 48)
		
		with self.subTest("encode"):
			test_data = [(0, struct.pack("<LH", 0, 0))]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.encode(x), y)
			
			with self.assertRaises(ValueError):
				variable.encode(-0.1)
		
		with self.subTest("decode"):
			test_data = [(struct.pack("<LH", 0, 0), 0),
				(struct.pack("<LH", 10 * 60 * 60 * 1000, 0), 10 * 60 * 60),
				(struct.pack("<LH", 0, 366), 366 * 24 * 60 * 60)]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.decode(x), y)
	
	def test_domain(self):
		variable = Variable("DOMAIN", 100, 0, DOMAIN)
		
		self.assertEqual(variable.size, 0)
		
		with self.subTest("encode"):
			test_data = [(b"\xA5\x5A", b"\xA5\x5A")]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.encode(x), y)
		
		with self.subTest("decode"):
			test_data = [(b"\xA5\x5A", b"\xA5\x5A")]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.decode(x), y)
	
	def test_integer24(self):
		variable = Variable("INTEGER24", 100, 0, INTEGER24)
		
		self.assertEqual(variable.size, 24)
		
		with self.subTest("encode"):
			test_data = [(0, b"\x00\x00\x00"),
				(5614165, b"\x55\xAA\x55"),
				(-5614166, b"\xAA\x55\xAA")]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.encode(x), y)
			
			test_data = [-2 ** 23 - 1, 2 ** 23]
			for x in test_data:
				with self.subTest("x=" + str(x)):
					with self.assertRaises(ValueError):
						variable.encode(x)
		
		with self.subTest("decode"):
			test_data = [(b"\x00\x00\x00", 0),
				(b"\x55\xAA\x55", 5614165),
				(b"\xAA\x55\xAA", -5614166),
				(b"\x55\xAA\x55\xFF", 5614165),
				(b"\xAA\x55\xAA\x00", -5614166)]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.decode(x), y)
			
			test_data = [b"\x00"]
			for x in test_data:
				with self.subTest("x=" + str(x)):
					with self.assertRaises(ValueError):
						variable.decode(x)
	
	def test_real64(self):
		variable = Variable("REAL64", 100, 0, REAL64)
		
		self.assertEqual(variable.size, 64)
		
		with self.subTest("encode"):
			test_data = [(0.0, b"\x00\x00\x00\x00\x00\x00\x00\x00")]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.encode(x), y)
		
		with self.subTest("decode"):
			test_data = [(b"\x00\x00\x00\x00\x00\x00\x00\x00", 0.0)]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.decode(x), y)
			
			test_data = [b"\x00"]
			for x in test_data:
				with self.subTest("x=" + str(x)):
					with self.assertRaises(ValueError):
						variable.decode(x)
	
	def test_integer40(self):
		variable = Variable("INTEGER40", 100, 0, INTEGER40)
		
		self.assertEqual(variable.size, 40)
		
		with self.subTest("encode"):
			test_data = [(0, b"\x00\x00\x00\x00\x00"),
				(367929961045, b"\x55\xAA\x55\xAA\x55"),
				(-367929961046, b"\xAA\x55\xAA\x55\xAA")]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.encode(x), y)
			
			test_data = [-2 ** 39 - 1, 2 ** 39]
			for x in test_data:
				with self.subTest("x=" + str(x)):
					with self.assertRaises(ValueError):
						variable.encode(x)
		
		with self.subTest("decode"):
			test_data = [(b"\x00\x00\x00\x00\x00", 0),
				(b"\x55\xAA\x55\xAA\x55", 367929961045),
				(b"\xAA\x55\xAA\x55\xAA", -367929961046),
				(b"\x55\xAA\x55\xAA\x55\xFF", 367929961045),
				(b"\xAA\x55\xAA\x55\xAA\x00", -367929961046)]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.decode(x), y)
			
			test_data = [b"\x00"]
			for x in test_data:
				with self.subTest("x=" + str(x)):
					with self.assertRaises(ValueError):
						variable.decode(x)
	
	def test_integer48(self):
		variable = Variable("INTEGER48", 100, 0, INTEGER48)
		
		self.assertEqual(variable.size, 48)
		
		with self.subTest("encode"):
			test_data = [(0, b"\x00\x00\x00\x00\x00\x00"),
				(-94190070027691, b"\x55\xAA\x55\xAA\x55\xAA"),
				(94190070027690, b"\xAA\x55\xAA\x55\xAA\x55")]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.encode(x), y)
			
			test_data = [-2 ** 47 - 1, 2 ** 47]
			for x in test_data:
				with self.subTest("x=" + str(x)):
					with self.assertRaises(ValueError):
						variable.encode(x)
		
		with self.subTest("decode"):
			test_data = [(b"\x00\x00\x00\x00\x00\x00", 0),
				(b"\x55\xAA\x55\xAA\x55\xAA", -94190070027691),
				(b"\xAA\x55\xAA\x55\xAA\x55", 94190070027690),
				(b"\x55\xAA\x55\xAA\x55\xAA\x00", -94190070027691),
				(b"\xAA\x55\xAA\x55\xAA\x55\xFF", 94190070027690)]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.decode(x), y)
			
			test_data = [b"\x00"]
			for x in test_data:
				with self.subTest("x=" + str(x)):
					with self.assertRaises(ValueError):
						variable.decode(x)
	
	def test_integer56(self):
		variable = Variable("INTEGER56", 100, 0, INTEGER56)
		
		self.assertEqual(variable.size, 56)
		
		with self.subTest("encode"):
			test_data = [(0, b"\x00\x00\x00\x00\x00\x00\x00"),
				(24112657927088725, b"\x55\xAA\x55\xAA\x55\xAA\x55"),
				(-24112657927088726, b"\xAA\x55\xAA\x55\xAA\x55\xAA")]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.encode(x), y)
			
			test_data = [-2 ** 55 - 1, 2 ** 55]
			for x in test_data:
				with self.subTest("x=" + str(x)):
					with self.assertRaises(ValueError):
						variable.encode(x)
		
		with self.subTest("decode"):
			test_data = [(b"\x00\x00\x00\x00\x00\x00\x00", 0),
				(b"\x55\xAA\x55\xAA\x55\xAA\x55", 24112657927088725),
				(b"\xAA\x55\xAA\x55\xAA\x55\xAA", -24112657927088726),
				(b"\x55\xAA\x55\xAA\x55\xAA\x55\xFF", 24112657927088725),
				(b"\xAA\x55\xAA\x55\xAA\x55\xAA\x00", -24112657927088726)]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.decode(x), y)
			
			test_data = [b"\x00"]
			for x in test_data:
				with self.subTest("x=" + str(x)):
					with self.assertRaises(ValueError):
						variable.decode(x)
	
	def test_integer64(self):
		variable = Variable("INTEGER64", 100, 0, INTEGER64)
		
		self.assertEqual(variable.size, 64)
		
		with self.subTest("encode"):
			test_data = [(0, b"\x00\x00\x00\x00\x00\x00\x00\x00"),
				(-6172840429334713771, b"\x55\xAA\x55\xAA\x55\xAA\x55\xAA"),
				(6172840429334713770, b"\xAA\x55\xAA\x55\xAA\x55\xAA\x55")]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.encode(x), y)
			
			test_data = [-2 ** 63 - 1, 2 ** 63]
			for x in test_data:
				with self.subTest("x=" + str(x)):
					with self.assertRaises(ValueError):
						variable.encode(x)
		
		with self.subTest("decode"):
			test_data = [(b"\x00\x00\x00\x00\x00\x00\x00\x00", 0),
				(b"\x55\xAA\x55\xAA\x55\xAA\x55\xAA", -6172840429334713771),
				(b"\xAA\x55\xAA\x55\xAA\x55\xAA\x55", 6172840429334713770),
				(b"\x55\xAA\x55\xAA\x55\xAA\x55\xAA\xFF", -6172840429334713771),
				(b"\xAA\x55\xAA\x55\xAA\x55\xAA\x55\xFF", 6172840429334713770)]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.decode(x), y)
			
			test_data = [b"\x00"]
			for x in test_data:
				with self.subTest("x=" + str(x)):
					with self.assertRaises(ValueError):
						variable.decode(x)
	
	def test_unsigned24(self):
		variable = Variable("UNSIGNED24", 100, 0, UNSIGNED24)
		
		self.assertEqual(variable.size, 24)
		
		with self.subTest("encode"):
			test_data = [(0, b"\x00\x00\x00"),
				(5614165, b"\x55\xAA\x55"),
				(11163050, b"\xAA\x55\xAA")]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.encode(x), y)
			
			test_data = [-1, 2 ** 24]
			for x in test_data:
				with self.subTest("x=" + str(x)):
					with self.assertRaises(ValueError):
						variable.encode(x)
		
		with self.subTest("decode"):
			test_data = [(b"\x00\x00\x00", 0),
				(b"\x55\xAA\x55", 5614165),
				(b"\xAA\x55\xAA", 11163050),
				(b"\x55\xAA\x55\xFF", 5614165),
				(b"\xAA\x55\xAA\xFF", 11163050)]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.decode(x), y)
			
			test_data = [b"\x00"]
			for x in test_data:
				with self.subTest("x=" + str(x)):
					with self.assertRaises(ValueError):
						variable.decode(x)
		
	def test_unsigned40(self):	
		variable = Variable("UNSIGNED40", 100, 0, UNSIGNED40)
		
		self.assertEqual(variable.size, 40)
		
		with self.subTest("encode"):
			test_data = [(0, b"\x00\x00\x00\x00\x00"),
				(367929961045, b"\x55\xAA\x55\xAA\x55"),
				(731581666730, b"\xAA\x55\xAA\x55\xAA")]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.encode(x), y)
			
			test_data = [-1, 2 ** 40]
			for x in test_data:
				with self.subTest("x=" + str(x)):
					with self.assertRaises(ValueError):
						variable.encode(x)
		
		with self.subTest("decode"):
			test_data = [(b"\x00\x00\x00\x00\x00", 0),
				(b"\x55\xAA\x55\xAA\x55", 367929961045),
				(b"\xAA\x55\xAA\x55\xAA", 731581666730),
				(b"\x55\xAA\x55\xAA\x55\xFF", 367929961045),
				(b"\xAA\x55\xAA\x55\xAA\xFF", 731581666730)]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.decode(x), y)
			
			test_data = [b"\x00"]
			for x in test_data:
				with self.subTest("x=" + str(x)):
					with self.assertRaises(ValueError):
						variable.decode(x)
	
	def test_unsigned48(self):
		variable = Variable("UNSIGNED48", 100, 0, UNSIGNED48)
		
		self.assertEqual(variable.size, 48)
		
		with self.subTest("encode"):
			test_data = [(0, b"\x00\x00\x00\x00\x00\x00"),
				(187284906682965, b"\x55\xAA\x55\xAA\x55\xAA"),
				(94190070027690, b"\xAA\x55\xAA\x55\xAA\x55")]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.encode(x), y)
			
			test_data = [-1, 2 ** 48]
			for x in test_data:
				with self.subTest("x=" + str(x)):
					with self.assertRaises(ValueError):
						variable.encode(x)
		
		with self.subTest("decode"):
			test_data = [(b"\x00\x00\x00\x00\x00\x00", 0),
				(b"\x55\xAA\x55\xAA\x55\xAA", 187284906682965),
				(b"\xAA\x55\xAA\x55\xAA\x55", 94190070027690),
				(b"\x55\xAA\x55\xAA\x55\xAA\xFF", 187284906682965),
				(b"\xAA\x55\xAA\x55\xAA\x55\x55", 94190070027690)]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.decode(x), y)
			
			test_data = [b"\x00"]
			for x in test_data:
				with self.subTest("x=" + str(x)):
					with self.assertRaises(ValueError):
						variable.decode(x)
	
	def test_unsigned56(self):
		variable = Variable("UNSIGNED56", 100, 0, UNSIGNED56)
		
		self.assertEqual(variable.size, 56)
		
		with self.subTest("encode"):
			test_data = [(0, b"\x00\x00\x00\x00\x00\x00\x00"),
				(24112657927088725, b"\x55\xAA\x55\xAA\x55\xAA\x55"),
				(47944936110839210, b"\xAA\x55\xAA\x55\xAA\x55\xAA")]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.encode(x), y)
			
			test_data = [-1, 2 ** 56]
			for x in test_data:
				with self.subTest("x=" + str(x)):
					with self.assertRaises(ValueError):
						variable.encode(x)
		
		with self.subTest("decode"):
			test_data = [(b"\x00\x00\x00\x00\x00\x00\x00", 0),
				(b"\x55\xAA\x55\xAA\x55\xAA\x55", 24112657927088725),
				(b"\xAA\x55\xAA\x55\xAA\x55\xAA", 47944936110839210),
				(b"\x55\xAA\x55\xAA\x55\xAA\x55\xFF", 24112657927088725),
				(b"\xAA\x55\xAA\x55\xAA\x55\xAA\x55", 47944936110839210)]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.decode(x), y)
			
			test_data = [b"\x00"]
			for x in test_data:
				with self.subTest("x=" + str(x)):
					with self.assertRaises(ValueError):
						variable.decode(x)
	
	def test_unsigned64(self):
		variable = Variable("UNSIGNED64", 100, 0, UNSIGNED64)
		
		self.assertEqual(variable.size, 64)
		
		with self.subTest("encode"):
			test_data = [(0, b"\x00\x00\x00\x00\x00\x00\x00\x00"),
				(12273903644374837845, b"\x55\xAA\x55\xAA\x55\xAA\x55\xAA"),
				(6172840429334713770, b"\xAA\x55\xAA\x55\xAA\x55\xAA\x55")]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.encode(x), y)
			
			test_data = [-1, 2 ** 64]
			for x in test_data:
				with self.subTest("x=" + str(x)):
					with self.assertRaises(ValueError):
						variable.encode(x)
		
		with self.subTest("decode"):
			test_data = [(b"\x00\x00\x00\x00\x00\x00\x00\x00", 0),
				(b"\x55\xAA\x55\xAA\x55\xAA\x55\xAA", 12273903644374837845),
				(b"\xAA\x55\xAA\x55\xAA\x55\xAA\x55", 6172840429334713770),
				(b"\x55\xAA\x55\xAA\x55\xAA\x55\xAA\xFF", 12273903644374837845),
				(b"\xAA\x55\xAA\x55\xAA\x55\xAA\x55\x55", 6172840429334713770)]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.decode(x), y)
			
			test_data = [b"\x00"]
			for x in test_data:
				with self.subTest("x=" + str(x)):
					with self.assertRaises(ValueError):
						variable.decode(x)


if __name__ == "__main__":
	unittest.main()
