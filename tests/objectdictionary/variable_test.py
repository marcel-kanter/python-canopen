import unittest
import struct
import calendar
import canopen.objectdictionary
from canopen.objectdictionary.datatypes import *


class VariableTestCase(unittest.TestCase):
	def test_init(self):
		with self.assertRaises(ValueError):
			canopen.objectdictionary.Variable("var", -1, 0, canopen.objectdictionary.UNSIGNED32)
		with self.assertRaises(ValueError):
			canopen.objectdictionary.Variable("var", 65536, 0, canopen.objectdictionary.UNSIGNED32)
		with self.assertRaises(ValueError):
			canopen.objectdictionary.Variable("var", 0, -1, canopen.objectdictionary.UNSIGNED32)
		with self.assertRaises(ValueError):
			canopen.objectdictionary.Variable("var", 0, 256, canopen.objectdictionary.UNSIGNED32)
		with self.assertRaises(ValueError):
			canopen.objectdictionary.Variable("var", 0, 0, 0)
		with self.assertRaises(ValueError):
			canopen.objectdictionary.Variable("var", 0, 0, canopen.objectdictionary.UNSIGNED32, "X")
		
		for access_type in ["rw", "wo", "ro", "const"]:
			examinee = canopen.objectdictionary.Variable("var", 100, 0, UNSIGNED32, access_type)
			self.assertEqual(examinee.access_type, access_type)
		
		name = "var"
		index = 100
		subindex = 0
		data_type = canopen.objectdictionary.UNSIGNED32
		access_type = "rw"
		description = "abc"
		examinee = canopen.objectdictionary.Variable(name, index, subindex, data_type, access_type, description)
		
		self.assertEqual(examinee.object_type, 7)
		self.assertEqual(examinee.name, name)
		self.assertEqual(examinee.index, index)
		self.assertEqual(examinee.subindex, subindex)
		self.assertEqual(examinee.default_value, 0)
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
				
		examinee.access_type = "wo"
		self.assertEqual(examinee.access_type, "wo")
		examinee.access_type = "ro"
		self.assertEqual(examinee.access_type, "ro")
		
		examinee.default_value = 100
		self.assertEqual(examinee.default_value, 100)
		
		for data_type in [BOOLEAN, INTEGER8, INTEGER16, INTEGER32, UNSIGNED8, UNSIGNED16, UNSIGNED32, REAL32, VISIBLE_STRING, OCTET_STRING, UNICODE_STRING, TIME_OF_DAY, TIME_DIFFERENCE, DOMAIN, INTEGER24, REAL64, INTEGER40, INTEGER48, INTEGER56, INTEGER64, UNSIGNED24, UNSIGNED40, UNSIGNED48, UNSIGNED56, UNSIGNED64]:
			examinee = canopen.objectdictionary.Variable("var", 100, 0, data_type)
			self.assertEqual(examinee.data_type, data_type)
			self.assertEqual(examinee.default_value, examinee.decode(examinee.encode(examinee.default_value)))
		
		desc = "Franz jagt im komplett verwahrlosten Taxi quer durch Bayern."
		examinee.description = desc
		self.assertEqual(examinee.description, desc)
	
	def test_equals(self):
		a = canopen.objectdictionary.Variable("var", 100, 0, UNSIGNED32, "rw")
		
		#### Test step: Reflexivity
		self.assertTrue(a == a)
		
		#### Test step: Compare same classes only (required for transitivity)
		test_data = [None, 3, canopen.objectdictionary.DefType("var", 100)]
		for value in test_data:
			with self.subTest("value=" + str(value)):
				self.assertFalse(a == value)
		
		#### Test step: Consistency
		b = canopen.objectdictionary.Variable("var", 100, 0, UNSIGNED32, "rw")
		for _ in range(3):
			self.assertTrue(a == b)
		
		#### Test step: Symmetricality, Contents
		b = canopen.objectdictionary.Variable("var", 100, 0, UNSIGNED32, "rw")
		self.assertTrue(a == b)
		self.assertEqual(a == b, b == a)
		
		b = canopen.objectdictionary.Variable("x", 100, 0, UNSIGNED32, "rw")
		self.assertFalse(a == b)
		self.assertEqual(a == b, b == a)
		
		b = canopen.objectdictionary.Variable("var", 111, 0, UNSIGNED32, "rw")
		self.assertFalse(a == b)
		self.assertEqual(a == b, b == a)
		
		b = canopen.objectdictionary.Variable("var", 100, 1, UNSIGNED32, "rw")
		self.assertFalse(a == b)
		self.assertEqual(a == b, b == a)
		
		b = canopen.objectdictionary.Variable("var", 100, 0, BOOLEAN, "rw")
		self.assertFalse(a == b)
		self.assertEqual(a == b, b == a)
		
		b = canopen.objectdictionary.Variable("var", 100, 0, UNSIGNED32, "ro")
		self.assertFalse(a == b)
		self.assertEqual(a == b, b == a)
		
		b = canopen.objectdictionary.Variable("var", 100, 0, UNSIGNED32, "rw")
		b.default_value = 10
		self.assertFalse(a == b)
		self.assertEqual(a == b, b == a)
		
		b = canopen.objectdictionary.Variable("var", 100, 0, UNSIGNED32, "rw")
		b.description = a.description + "XXX"
		self.assertFalse(a == b)
		self.assertEqual(a == b, b == a)
	
	def test_boolean(self):
		variable = canopen.objectdictionary.Variable("BOOLEAN", 100, 0, canopen.objectdictionary.BOOLEAN)
		
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
		variable = canopen.objectdictionary.Variable("INTEGER8", 100, 0, canopen.objectdictionary.INTEGER8)
		
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
		variable = canopen.objectdictionary.Variable("INTEGER16", 100, 0, canopen.objectdictionary.INTEGER16)
		
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
		variable = canopen.objectdictionary.Variable("INTEGER32", 100, 0, canopen.objectdictionary.INTEGER32)
		
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
		variable = canopen.objectdictionary.Variable("UNSIGNED8", 100, 0, canopen.objectdictionary.UNSIGNED8)
		
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
		variable = canopen.objectdictionary.Variable("UNSIGNED16", 100, 0, canopen.objectdictionary.UNSIGNED16)
		
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
		variable = canopen.objectdictionary.Variable("UNSIGNED32", 100, 0, canopen.objectdictionary.UNSIGNED32)
		
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
		variable = canopen.objectdictionary.Variable("REAL32", 100, 0, canopen.objectdictionary.REAL32)
		
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
		variable = canopen.objectdictionary.Variable("VISIBLE_STRING", 100, 0, canopen.objectdictionary.VISIBLE_STRING)
		
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
		variable = canopen.objectdictionary.Variable("OCTET_STRING", 100, 0, canopen.objectdictionary.OCTET_STRING)
		
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
		variable = canopen.objectdictionary.Variable("UNICODE_STRING", 100, 0, canopen.objectdictionary.UNICODE_STRING)
		
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
		variable = canopen.objectdictionary.Variable("TIME_OF_DAY", 100, 0, canopen.objectdictionary.TIME_OF_DAY)
		
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
		variable = canopen.objectdictionary.Variable("TIME_DIFFERENCE", 100, 0, canopen.objectdictionary.TIME_DIFFERENCE)
		
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
		variable = canopen.objectdictionary.Variable("DOMAIN", 100, 0, canopen.objectdictionary.DOMAIN)
		
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
		variable = canopen.objectdictionary.Variable("INTEGER24", 100, 0, canopen.objectdictionary.INTEGER24)
		
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
		variable = canopen.objectdictionary.Variable("REAL64", 100, 0, canopen.objectdictionary.REAL64)
		
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
		variable = canopen.objectdictionary.Variable("INTEGER40", 100, 0, canopen.objectdictionary.INTEGER40)
		
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
		variable = canopen.objectdictionary.Variable("INTEGER48", 100, 0, canopen.objectdictionary.INTEGER48)
		
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
		variable = canopen.objectdictionary.Variable("INTEGER56", 100, 0, canopen.objectdictionary.INTEGER56)
		
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
		variable = canopen.objectdictionary.Variable("INTEGER64", 100, 0, canopen.objectdictionary.INTEGER64)
		
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
		variable = canopen.objectdictionary.Variable("UNSIGNED24", 100, 0, canopen.objectdictionary.UNSIGNED24)
		
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
		variable = canopen.objectdictionary.Variable("UNSIGNED40", 100, 0, canopen.objectdictionary.UNSIGNED40)
		
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
		variable = canopen.objectdictionary.Variable("UNSIGNED48", 100, 0, canopen.objectdictionary.UNSIGNED48)
		
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
		variable = canopen.objectdictionary.Variable("UNSIGNED56", 100, 0, canopen.objectdictionary.UNSIGNED56)
		
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
		variable = canopen.objectdictionary.Variable("UNSIGNED64", 100, 0, canopen.objectdictionary.UNSIGNED64)
		
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
