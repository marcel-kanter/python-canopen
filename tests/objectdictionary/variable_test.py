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
		variable = canopen.objectdictionary.Variable(name, index, subindex, data_type, access_type)
		
		self.assertEqual(variable.object_type, 7)
		self.assertEqual(variable.name, name)
		self.assertEqual(variable.index, index)
		self.assertEqual(variable.subindex, subindex)
		self.assertEqual(variable.default_value, 0)
		
		with self.assertRaises(AttributeError):
			variable.name = name
		with self.assertRaises(AttributeError):
			variable.index = index
		with self.assertRaises(AttributeError):
			variable.subindex = subindex
		with self.assertRaises(AttributeError):
			variable.data_type = data_type
		with self.assertRaises(ValueError):
			variable.access_type = "xx"
				
		variable.access_type = "wo"
		self.assertEqual(variable.access_type, "wo")
		variable.access_type = "ro"
		self.assertEqual(variable.access_type, "ro")
		
		variable.default_value = 100
		self.assertEqual(variable.default_value, 100)
		
		for data_type in [BOOLEAN, INTEGER8, INTEGER16, INTEGER32, UNSIGNED8, UNSIGNED16, UNSIGNED32, REAL32, VISIBLE_STRING, OCTET_STRING, UNICODE_STRING, TIME_OF_DAY, TIME_DIFFERENCE, DOMAIN, INTEGER24, REAL64, INTEGER40, INTEGER48, INTEGER56, INTEGER64, UNSIGNED24, UNSIGNED40, UNSIGNED48, UNSIGNED56, UNSIGNED64]:
			examinee = canopen.objectdictionary.Variable("var", 100, 0, data_type)
			self.assertEqual(examinee.data_type, data_type)
			self.assertEqual(examinee.default_value, examinee.decode(examinee.encode(examinee.default_value)))
	
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
	
	def test_encode(self):
		with self.subTest("datatype=BOOLEAN"):
			variable = canopen.objectdictionary.Variable("BOOLEAN", 100, 0, canopen.objectdictionary.BOOLEAN)
			test_data = [(False, b"\x00"),
				(True, b"\x01")]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.encode(x), y)
		
		with self.subTest("datatype=INTEGER8"):
			variable = canopen.objectdictionary.Variable("INTEGER8", 100, 0, canopen.objectdictionary.INTEGER8)
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
		
		with self.subTest("datatype=INTEGER16"):
			variable = canopen.objectdictionary.Variable("INTEGER16", 100, 0, canopen.objectdictionary.INTEGER16)
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
		
		with self.subTest("datatype=INTEGER32"):
			variable = canopen.objectdictionary.Variable("INTEGER32", 100, 0, canopen.objectdictionary.INTEGER32)
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
		
		with self.subTest("datatype=UNSIGNED8"):
			variable = canopen.objectdictionary.Variable("UNSIGNED8", 100, 0, canopen.objectdictionary.UNSIGNED8)
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
		
		with self.subTest("datatype=UNSIGNED16"):
			variable = canopen.objectdictionary.Variable("UNSIGNED16", 100, 0, canopen.objectdictionary.UNSIGNED16)
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
		
		with self.subTest("datatype=UNSIGNED32"):
			variable = canopen.objectdictionary.Variable("UNSIGNED32", 100, 0, canopen.objectdictionary.UNSIGNED32)
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
		
		with self.subTest("datatype=REAL32"):
			variable = canopen.objectdictionary.Variable("REAL32", 100, 0, canopen.objectdictionary.REAL32)
			test_data = [(0.0, b"\x00\x00\x00\x00")]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.encode(x), y)
		
		with self.subTest("datatype=VISIBLE_STRING"):
			variable = canopen.objectdictionary.Variable("VISIBLE_STRING", 100, 0, canopen.objectdictionary.VISIBLE_STRING)
			test_data = [("TEXT", b"TEXT")]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.encode(x), y)
		
		with self.subTest("datatype=OCTET_STRING"):
			variable = canopen.objectdictionary.Variable("OCTET_STRING", 100, 0, canopen.objectdictionary.OCTET_STRING)
			test_data = [("TEXT", b"TEXT")]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.encode(x), y)
		
		with self.subTest("datatype=UNICODE_STRING"):
			variable = canopen.objectdictionary.Variable("UNICODE_STRING", 100, 0, canopen.objectdictionary.UNICODE_STRING)
			test_data = [("TEXT", b"T\x00E\x00X\x00T\x00")]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.encode(x), y)
		
		with self.subTest("datatype=TIME_OF_DAY"):
			variable = canopen.objectdictionary.Variable("TIME_OF_DAY", 100, 0, canopen.objectdictionary.TIME_OF_DAY)
			test_data = [(calendar.timegm((1984, 1, 1, 0, 0, 0)), struct.pack("<LH", 0, 0))]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.encode(x), y)
			
			with self.assertRaises(ValueError):
				variable.encode(0)
		
		with self.subTest("datatype=TIME_DIFFERENCE"):
			variable = canopen.objectdictionary.Variable("TIME_DIFFERENCE", 100, 0, canopen.objectdictionary.TIME_DIFFERENCE)
			test_data = [(0, struct.pack("<LH", 0, 0))]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.encode(x), y)
			
			with self.assertRaises(ValueError):
				variable.encode(-0.1)
		
		with self.subTest("datatype=DOMAIN"):
			variable = canopen.objectdictionary.Variable("DOMAIN", 100, 0, canopen.objectdictionary.DOMAIN)
			test_data = [(b"\xA5\x5A", b"\xA5\x5A")]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.encode(x), y)
		
		with self.subTest("datatype=INTEGER24"):
			variable = canopen.objectdictionary.Variable("INTEGER24", 100, 0, canopen.objectdictionary.INTEGER24)
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
		
		with self.subTest("datatype=REAL64"):
			variable = canopen.objectdictionary.Variable("REAL64", 100, 0, canopen.objectdictionary.REAL64)
			test_data = [(0.0, b"\x00\x00\x00\x00\x00\x00\x00\x00")]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.encode(x), y)
		
		with self.subTest("datatype=INTEGER40"):
			variable = canopen.objectdictionary.Variable("INTEGER40", 100, 0, canopen.objectdictionary.INTEGER40)
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
		
		with self.subTest("datatype=INTEGER48"):
			variable = canopen.objectdictionary.Variable("INTEGER48", 100, 0, canopen.objectdictionary.INTEGER48)
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
		
		with self.subTest("datatype=INTEGER56"):
			variable = canopen.objectdictionary.Variable("INTEGER56", 100, 0, canopen.objectdictionary.INTEGER56)
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
		
		with self.subTest("datatype=INTEGER64"):
			variable = canopen.objectdictionary.Variable("INTEGER64", 100, 0, canopen.objectdictionary.INTEGER64)
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
		
		with self.subTest("datatype=UNSIGNED24"):
			variable = canopen.objectdictionary.Variable("UNSIGNED24", 100, 0, canopen.objectdictionary.UNSIGNED24)
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
		
		with self.subTest("datatype=UNSIGNED40"):
			variable = canopen.objectdictionary.Variable("UNSIGNED40", 100, 0, canopen.objectdictionary.UNSIGNED40)
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
		
		with self.subTest("datatype=UNSIGNED48"):
			variable = canopen.objectdictionary.Variable("UNSIGNED48", 100, 0, canopen.objectdictionary.UNSIGNED48)
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
		
		with self.subTest("datatype=UNSIGNED56"):
			variable = canopen.objectdictionary.Variable("UNSIGNED56", 100, 0, canopen.objectdictionary.UNSIGNED56)
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
		
		with self.subTest("datatype=UNSIGNED64"):
			variable = canopen.objectdictionary.Variable("UNSIGNED64", 100, 0, canopen.objectdictionary.UNSIGNED64)
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
	
	def test_decode(self):
		with self.subTest("datatype=BOOLEAN"):
			variable = canopen.objectdictionary.Variable("BOOLEAN", 100, 0, canopen.objectdictionary.BOOLEAN)
			test_data = [(b"\x00", False),
				(b"\x01", True),
				(b"\x01\x00", True),
				(b"\x00\x00", False)]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.decode(x), y)
		
		with self.subTest("datatype=INTEGER8"):
			variable = canopen.objectdictionary.Variable("INTEGER8", 100, 0, canopen.objectdictionary.INTEGER8)
			test_data = [(b"\x00", 0),
				(b"\x55", 85),
				(b"\xAA", -86),
				(b"\x55\xFF", 85),
				(b"\xAA\x00", -86)]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.decode(x), y)
		
		with self.subTest("datatype=INTEGER16"):
			variable = canopen.objectdictionary.Variable("INTEGER16", 100, 0, canopen.objectdictionary.INTEGER16)
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
		
		with self.subTest("datatype=INTEGER32"):
			variable = canopen.objectdictionary.Variable("INTEGER32", 100, 0, canopen.objectdictionary.INTEGER32)
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
		
		with self.subTest("datatype=UNSIGNED8"):
			variable = canopen.objectdictionary.Variable("UNSIGNED8", 100, 0, canopen.objectdictionary.UNSIGNED8)
			test_data = [(b"\x00", 0),
				(b"\x55", 85),
				(b"\xAA", 170),
				(b"\x55\xFF", 85),
				(b"\xAA\xFF", 170)]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.decode(x), y)
		
		with self.subTest("datatype=UNSIGNED16"):
			variable = canopen.objectdictionary.Variable("UNSIGNED16", 100, 0, canopen.objectdictionary.UNSIGNED16)
			test_data = [(b"\x00\x00", 0),
				(b"\x55\xAA",  43605),
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
		
		with self.subTest("datatype=UNSIGNED32"):
			variable = canopen.objectdictionary.Variable("UNSIGNED32", 100, 0, canopen.objectdictionary.UNSIGNED32)
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
		
		with self.subTest("datatype=REAL32"):
			variable = canopen.objectdictionary.Variable("REAL32", 100, 0, canopen.objectdictionary.REAL32)
			test_data = [(b"\x00\x00\x00\x00", 0.0)]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.decode(x), y)
			
			test_data = [b"\x00"]
			for x in test_data:
				with self.subTest("x=" + str(x)):
					with self.assertRaises(ValueError):
						variable.decode(x)
		
		with self.subTest("datatype=VISIBLE_STRING"):
			variable = canopen.objectdictionary.Variable("VISIBLE_STRING", 100, 0, canopen.objectdictionary.VISIBLE_STRING)
			test_data = [(b"TEXT", "TEXT")]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.decode(x), y)
		
		with self.subTest("datatype=OCTET_STRING"):
			variable = canopen.objectdictionary.Variable("OCTET_STRING", 100, 0, canopen.objectdictionary.OCTET_STRING)
			test_data = [(b"TEXT", "TEXT")]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.decode(x), y)
		
		with self.subTest("datatype=UNICODE_STRING"):
			variable = canopen.objectdictionary.Variable("UNICODE_STRING", 100, 0, canopen.objectdictionary.UNICODE_STRING)
			test_data = [(b"T\x00E\x00X\x00T\x00", "TEXT")]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.decode(x), y)
		
		with self.subTest("datatype=TIME_OF_DAY"):
			variable = canopen.objectdictionary.Variable("TIME_OF_DAY", 100, 0, canopen.objectdictionary.TIME_OF_DAY)
			test_data = [(struct.pack("<LH", 0, 0), calendar.timegm((1984, 1, 1, 0, 0, 0))),
				(struct.pack("<LH", 10 * 60 * 60 * 1000, 0), calendar.timegm((1984, 1, 1, 10, 0, 0))),
				(struct.pack("<LH", 0, 366), calendar.timegm((1985, 1, 1, 0, 0, 0)))]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.decode(x), y)
		
		with self.subTest("datatype=TIME_DIFFERENCE"):
			variable = canopen.objectdictionary.Variable("TIME_DIFFERENCE", 100, 0, canopen.objectdictionary.TIME_DIFFERENCE)
			test_data = [(struct.pack("<LH", 0, 0), 0),
				(struct.pack("<LH", 10 * 60 * 60 * 1000, 0), 10 * 60 * 60),
				(struct.pack("<LH", 0, 366), 366 * 24 * 60 * 60)]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.decode(x), y)
		
		with self.subTest("datatype=DOMAIN"):
			variable = canopen.objectdictionary.Variable("DOMAIN", 100, 0, canopen.objectdictionary.DOMAIN)
			test_data = [(b"\xA5\x5A", b"\xA5\x5A")]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.decode(x), y)
		
		with self.subTest("datatype=INTEGER24"):
			variable = canopen.objectdictionary.Variable("INTEGER24", 100, 0, canopen.objectdictionary.INTEGER24)
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
		
		with self.subTest("datatype=REAL64"):
			variable = canopen.objectdictionary.Variable("REAL64", 100, 0, canopen.objectdictionary.REAL64)
			test_data = [(b"\x00\x00\x00\x00\x00\x00\x00\x00", 0.0)]
			for x, y in test_data:
				with self.subTest("x=" + str(x) + ",y=" + str(y)):
					self.assertEqual(variable.decode(x), y)
			
			test_data = [b"\x00"]
			for x in test_data:
				with self.subTest("x=" + str(x)):
					with self.assertRaises(ValueError):
						variable.decode(x)
		
		with self.subTest("datatype=INTEGER40"):
			variable = canopen.objectdictionary.Variable("INTEGER40", 100, 0, canopen.objectdictionary.INTEGER40)
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
		
		with self.subTest("datatype=INTEGER48"):
			variable = canopen.objectdictionary.Variable("INTEGER48", 100, 0, canopen.objectdictionary.INTEGER48)
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
		
		with self.subTest("datatype=INTEGER56"):
			variable = canopen.objectdictionary.Variable("INTEGER56", 100, 0, canopen.objectdictionary.INTEGER56)
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
		
		with self.subTest("datatype=INTEGER64"):
			variable = canopen.objectdictionary.Variable("INTEGER64", 100, 0, canopen.objectdictionary.INTEGER64)
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
		
		with self.subTest("datatype=UNSIGNED24"):
			variable = canopen.objectdictionary.Variable("UNSIGNED24", 100, 0, canopen.objectdictionary.UNSIGNED24)
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
		
		with self.subTest("datatype=UNSIGNED40"):
			variable = canopen.objectdictionary.Variable("UNSIGNED40", 100, 0, canopen.objectdictionary.UNSIGNED40)
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
		
		with self.subTest("datatype=UNSIGNED48"):
			variable = canopen.objectdictionary.Variable("UNSIGNED48", 100, 0, canopen.objectdictionary.UNSIGNED48)
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
		
		with self.subTest("datatype=UNSIGNED56"):
			variable = canopen.objectdictionary.Variable("UNSIGNED56", 100, 0, canopen.objectdictionary.UNSIGNED56)
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
		
		with self.subTest("datatype=UNSIGNED64"):
			variable = canopen.objectdictionary.Variable("UNSIGNED64", 100, 0, canopen.objectdictionary.UNSIGNED64)
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
