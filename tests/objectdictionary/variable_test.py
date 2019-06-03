import unittest
import canopen.objectdictionary


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
		
		name = "var"
		index = 100
		subindex = 0
		data_type = canopen.objectdictionary.UNSIGNED32
		access_type = "rw"
		variable = canopen.objectdictionary.Variable(name, index, subindex, data_type, access_type)
		
		self.assertEqual(variable.name, name)
		self.assertEqual(variable.index, index)
		self.assertEqual(variable.subindex, subindex)
		self.assertEqual(variable.data_type, data_type)
		self.assertEqual(variable.access_type, access_type)
		
		with self.assertRaises(AttributeError):
			variable.name = name
		with self.assertRaises(AttributeError):
			variable.index = index
		with self.assertRaises(AttributeError):
			variable.subindex = subindex
		with self.assertRaises(AttributeError):
			variable.data_type = data_type
		with self.assertRaises(AttributeError):
			variable.access_type = access_type
		
		canopen.objectdictionary.Variable("var", 100, 0, canopen.objectdictionary.UNSIGNED32, "r")
		canopen.objectdictionary.Variable("var", 100, 0, canopen.objectdictionary.UNSIGNED32, "w")
	
	def test_encode(self):
		variable = canopen.objectdictionary.Variable("BOOLEAN", 100, 0, canopen.objectdictionary.BOOLEAN)
		e = variable.encode(False)
		self.assertEqual(e, b"\x00")
		
		variable = canopen.objectdictionary.Variable("INTEGER8", 100, 0, canopen.objectdictionary.INTEGER8)
		e = variable.encode(0)
		self.assertEqual(e, b"\x00")
		with self.assertRaises(ValueError):
			variable.encode(-2 ** 7 - 1)
		with self.assertRaises(ValueError):
			variable.encode(2 ** 7)
		
		variable = canopen.objectdictionary.Variable("INTEGER16", 100, 0, canopen.objectdictionary.INTEGER16)
		e = variable.encode(0)
		self.assertEqual(e, b"\x00\x00")
		with self.assertRaises(ValueError):
			variable.encode(-2 ** 15 - 1)
		with self.assertRaises(ValueError):
			variable.encode(2 ** 15)
		
		variable = canopen.objectdictionary.Variable("INTEGER32", 100, 0, canopen.objectdictionary.INTEGER32)
		e = variable.encode(0)
		self.assertEqual(e, b"\x00\x00\x00\x00")
		with self.assertRaises(ValueError):
			variable.encode(-2 ** 31 - 1)
		with self.assertRaises(ValueError):
			variable.encode(2 ** 31)
		
		variable = canopen.objectdictionary.Variable("UNSIGNED8", 100, 0, canopen.objectdictionary.UNSIGNED8)
		e = variable.encode(0)
		self.assertEqual(e, b"\x00")
		with self.assertRaises(ValueError):
			variable.encode(-1)
		with self.assertRaises(ValueError):
			variable.encode(2 ** 8)
		
		variable = canopen.objectdictionary.Variable("UNSIGNED16", 100, 0, canopen.objectdictionary.UNSIGNED16)
		e = variable.encode(0)
		self.assertEqual(e, b"\x00\x00")
		with self.assertRaises(ValueError):
			variable.encode(-1)
		with self.assertRaises(ValueError):
			variable.encode(2 ** 16)
		
		variable = canopen.objectdictionary.Variable("UNSIGNED32", 100, 0, canopen.objectdictionary.UNSIGNED32)
		e = variable.encode(0)
		self.assertEqual(e, b"\x00\x00\x00\x00")
		with self.assertRaises(ValueError):
			variable.encode(-1)
		with self.assertRaises(ValueError):
			variable.encode(2 ** 32)
		
		variable = canopen.objectdictionary.Variable("REAL32", 100, 0, canopen.objectdictionary.REAL32)
		e = variable.encode(0.0)
		self.assertEqual(e, b"\x00\x00\x00\x00")
		
		variable = canopen.objectdictionary.Variable("VISIBLE_STRING", 100, 0, canopen.objectdictionary.VISIBLE_STRING)
		e = variable.encode("TEXT")
		self.assertEqual(e, b"TEXT")
		
		variable = canopen.objectdictionary.Variable("OCTET_STRING", 100, 0, canopen.objectdictionary.OCTET_STRING)
		e = variable.encode("TEXT")
		self.assertEqual(e, b"TEXT")
		
		variable = canopen.objectdictionary.Variable("UNICODE_STRING", 100, 0, canopen.objectdictionary.UNICODE_STRING)
		e = variable.encode("TEXT")
		self.assertEqual(e, b"T\x00E\x00X\x00T\x00")
		
		variable = canopen.objectdictionary.Variable("TIME_OF_DAY", 100, 0, canopen.objectdictionary.TIME_OF_DAY)
		with self.assertRaises(NotImplementedError):
			variable.encode(0.0)
		
		variable = canopen.objectdictionary.Variable("TIME_DIFFERENCE", 100, 0, canopen.objectdictionary.TIME_DIFFERENCE)
		with self.assertRaises(NotImplementedError):
			variable.encode(0.0)
		
		variable = canopen.objectdictionary.Variable("DOMAIN", 100, 0, canopen.objectdictionary.DOMAIN)
		e = variable.encode(b"\xA5\x5A")
		self.assertEqual(e, b"\xA5\x5A")
		
		variable = canopen.objectdictionary.Variable("INTEGER24", 100, 0, canopen.objectdictionary.INTEGER24)
		e = variable.encode(0)
		self.assertEqual(e, b"\x00\x00\x00")
		with self.assertRaises(ValueError):
			variable.encode(-2 ** 23 - 1)
		with self.assertRaises(ValueError):
			variable.encode(2 ** 23)
		
		variable = canopen.objectdictionary.Variable("REAL64", 100, 0, canopen.objectdictionary.REAL64)
		e = variable.encode(0.0)
		self.assertEqual(e, b"\x00\x00\x00\x00\x00\x00\x00\x00")
		
		variable = canopen.objectdictionary.Variable("INTEGER40", 100, 0, canopen.objectdictionary.INTEGER40)
		e = variable.encode(0)
		self.assertEqual(e, b"\x00\x00\x00\x00\x00")
		with self.assertRaises(ValueError):
			variable.encode(-2 ** 39 - 1)
		with self.assertRaises(ValueError):
			variable.encode(2 ** 39)
		
		variable = canopen.objectdictionary.Variable("INTEGER48", 100, 0, canopen.objectdictionary.INTEGER48)
		e = variable.encode(0)
		self.assertEqual(e, b"\x00\x00\x00\x00\x00\x00")
		with self.assertRaises(ValueError):
			variable.encode(-2 ** 47 - 1)
		with self.assertRaises(ValueError):
			variable.encode(2 ** 47)
		
		variable = canopen.objectdictionary.Variable("INTEGER56", 100, 0, canopen.objectdictionary.INTEGER56)
		e = variable.encode(0)
		self.assertEqual(e, b"\x00\x00\x00\x00\x00\x00\x00")
		with self.assertRaises(ValueError):
			variable.encode(-2 ** 55 - 1)
		with self.assertRaises(ValueError):
			variable.encode(2 ** 55)
		
		variable = canopen.objectdictionary.Variable("INTEGER64", 100, 0, canopen.objectdictionary.INTEGER64)
		e = variable.encode(0)
		self.assertEqual(e, b"\x00\x00\x00\x00\x00\x00\x00\x00")
		with self.assertRaises(ValueError):
			variable.encode(-2 ** 63 - 1)
		with self.assertRaises(ValueError):
			variable.encode(2 ** 63)
		
		variable = canopen.objectdictionary.Variable("UNSIGNED24", 100, 0, canopen.objectdictionary.UNSIGNED24)
		e = variable.encode(0)
		self.assertEqual(e, b"\x00\x00\x00")
		with self.assertRaises(ValueError):
			variable.encode(-1)
		with self.assertRaises(ValueError):
			variable.encode(2 ** 24)
		
		variable = canopen.objectdictionary.Variable("UNSIGNED40", 100, 0, canopen.objectdictionary.UNSIGNED40)
		e = variable.encode(0)
		self.assertEqual(e, b"\x00\x00\x00\x00\x00")
		with self.assertRaises(ValueError):
			variable.encode(-1)
		with self.assertRaises(ValueError):
			variable.encode(2 ** 40)
		
		variable = canopen.objectdictionary.Variable("UNSIGNED48", 100, 0, canopen.objectdictionary.UNSIGNED48)
		e = variable.encode(0)
		self.assertEqual(e, b"\x00\x00\x00\x00\x00\x00")
		with self.assertRaises(ValueError):
			variable.encode(-1)
		with self.assertRaises(ValueError):
			variable.encode(2 ** 48)
		
		variable = canopen.objectdictionary.Variable("UNSIGNED56", 100, 0, canopen.objectdictionary.UNSIGNED56)
		e = variable.encode(0)
		self.assertEqual(e, b"\x00\x00\x00\x00\x00\x00\x00")
		with self.assertRaises(ValueError):
			variable.encode(-1)
		with self.assertRaises(ValueError):
			variable.encode(2 ** 56)
		
		variable = canopen.objectdictionary.Variable("UNSIGNED64", 100, 0, canopen.objectdictionary.UNSIGNED64)
		e = variable.encode(0)
		self.assertEqual(e, b"\x00\x00\x00\x00\x00\x00\x00\x00")
		with self.assertRaises(ValueError):
			variable.encode(-1)
		with self.assertRaises(ValueError):
			variable.encode(2 ** 64)
	
	def test_decode(self):
		variable = canopen.objectdictionary.Variable("BOOLEAN", 100, 0, canopen.objectdictionary.BOOLEAN)
		d = variable.decode(b"\x00")
		self.assertEqual(d, False)
		
		variable = canopen.objectdictionary.Variable("INTEGER8", 100, 0, canopen.objectdictionary.INTEGER8)
		d = variable.decode(b"\x00")
		self.assertEqual(d, 0)
		
		variable = canopen.objectdictionary.Variable("INTEGER16", 100, 0, canopen.objectdictionary.INTEGER16)
		d = variable.decode(b"\x00\x00")
		self.assertEqual(d, 0)
		with self.assertRaises(ValueError):
			variable.decode(b"\x00")
		
		variable = canopen.objectdictionary.Variable("INTEGER32", 100, 0, canopen.objectdictionary.INTEGER32)
		d = variable.decode(b"\x00\x00\x00\x00")
		self.assertEqual(d, 0)
		with self.assertRaises(ValueError):
			variable.decode(b"\x00")
		
		variable = canopen.objectdictionary.Variable("UNSIGNED8", 100, 0, canopen.objectdictionary.UNSIGNED8)
		d = variable.decode(b"\x00")
		self.assertEqual(d, 0)
		
		variable = canopen.objectdictionary.Variable("UNSIGNED16", 100, 0, canopen.objectdictionary.UNSIGNED16)
		d = variable.decode(b"\x00\x00")
		self.assertEqual(d, 0)
		with self.assertRaises(ValueError):
			variable.decode(b"\x00")
		
		variable = canopen.objectdictionary.Variable("UNSIGNED32", 100, 0, canopen.objectdictionary.UNSIGNED32)
		d = variable.decode(b"\x00\x00\x00\x00")
		self.assertEqual(d, 0)
		with self.assertRaises(ValueError):
			variable.decode(b"\x00")
		
		variable = canopen.objectdictionary.Variable("REAL32", 100, 0, canopen.objectdictionary.REAL32)
		d = variable.decode(b"\x00\x00\x00\x00")
		self.assertEqual(d, 0.0)
		with self.assertRaises(ValueError):
			variable.decode(b"\x00")
		
		variable = canopen.objectdictionary.Variable("VISIBLE_STRING", 100, 0, canopen.objectdictionary.VISIBLE_STRING)
		d = variable.decode(b"TEXT")
		self.assertEqual(d, "TEXT")
		
		variable = canopen.objectdictionary.Variable("OCTET_STRING", 100, 0, canopen.objectdictionary.OCTET_STRING)
		d = variable.decode(b"TEXT")
		self.assertEqual(d, "TEXT")
		
		variable = canopen.objectdictionary.Variable("UNICODE_STRING", 100, 0, canopen.objectdictionary.UNICODE_STRING)
		d = variable.decode(b"T\x00E\x00X\x00T\x00")
		self.assertEqual(d, "TEXT")
		
		variable = canopen.objectdictionary.Variable("TIME_OF_DAY", 100, 0, canopen.objectdictionary.TIME_OF_DAY)
		with self.assertRaises(NotImplementedError):
			variable.decode(0.0)
		
		variable = canopen.objectdictionary.Variable("TIME_DIFFERENCE", 100, 0, canopen.objectdictionary.TIME_DIFFERENCE)
		with self.assertRaises(NotImplementedError):
			variable.decode(0.0)
		
		variable = canopen.objectdictionary.Variable("DOMAIN", 100, 0, canopen.objectdictionary.DOMAIN)
		d = variable.decode(b"\xA5\x5A")
		self.assertEqual(d, b"\xA5\x5A")
		
		variable = canopen.objectdictionary.Variable("INTEGER24", 100, 0, canopen.objectdictionary.INTEGER24)
		d = variable.decode(b"\x00\x00\x00")
		self.assertEqual(d, 0)
		with self.assertRaises(ValueError):
			variable.decode(b"\x00")
		
		variable = canopen.objectdictionary.Variable("REAL64", 100, 0, canopen.objectdictionary.REAL64)
		d = variable.decode(b"\x00\x00\x00\x00\x00\x00\x00\x00")
		self.assertEqual(d, 0.0)
		with self.assertRaises(ValueError):
			variable.decode(b"\x00")
		
		variable = canopen.objectdictionary.Variable("INTEGER40", 100, 0, canopen.objectdictionary.INTEGER40)
		d = variable.decode(b"\x00\x00\x00\x00\x00")
		self.assertEqual(d, 0)
		with self.assertRaises(ValueError):
			variable.decode(b"\x00")
		
		variable = canopen.objectdictionary.Variable("INTEGER48", 100, 0, canopen.objectdictionary.INTEGER48)
		d = variable.decode(b"\x00\x00\x00\x00\x00\x00")
		self.assertEqual(d, 0)
		with self.assertRaises(ValueError):
			variable.decode(b"\x00")
		
		variable = canopen.objectdictionary.Variable("INTEGER56", 100, 0, canopen.objectdictionary.INTEGER56)
		d = variable.decode(b"\x00\x00\x00\x00\x00\x00\x00")
		self.assertEqual(d, 0)
		with self.assertRaises(ValueError):
			variable.decode(b"\x00")
		
		variable = canopen.objectdictionary.Variable("INTEGER64", 100, 0, canopen.objectdictionary.INTEGER64)
		d = variable.decode(b"\x00\x00\x00\x00\x00\x00\x00\x00")
		self.assertEqual(d, 0)
		with self.assertRaises(ValueError):
			variable.decode(b"\x00")
		
		variable = canopen.objectdictionary.Variable("UNSIGNED24", 100, 0, canopen.objectdictionary.UNSIGNED24)
		d = variable.decode(b"\x00\x00\x00")
		self.assertEqual(d, 0)
		with self.assertRaises(ValueError):
			variable.decode(b"\x00")
		
		variable = canopen.objectdictionary.Variable("UNSIGNED40", 100, 0, canopen.objectdictionary.UNSIGNED40)
		d = variable.decode(b"\x00\x00\x00\x00\x00")
		self.assertEqual(d, 0)
		with self.assertRaises(ValueError):
			variable.decode(b"\x00")
		
		variable = canopen.objectdictionary.Variable("UNSIGNED48", 100, 0, canopen.objectdictionary.UNSIGNED48)
		d = variable.decode(b"\x00\x00\x00\x00\x00\x00")
		self.assertEqual(d, 0)
		with self.assertRaises(ValueError):
			variable.decode(b"\x00")
		
		variable = canopen.objectdictionary.Variable("UNSIGNED56", 100, 0, canopen.objectdictionary.UNSIGNED56)
		d = variable.decode(b"\x00\x00\x00\x00\x00\x00\x00")
		self.assertEqual(d, 0)
		with self.assertRaises(ValueError):
			variable.decode(b"\x00")
		
		variable = canopen.objectdictionary.Variable("UNSIGNED64", 100, 0, canopen.objectdictionary.UNSIGNED64)
		d = variable.decode(b"\x00\x00\x00\x00\x00\x00\x00\x00")
		self.assertEqual(d, 0)
		with self.assertRaises(ValueError):
			variable.decode(b"\x00")


if __name__ == "__main__":
	unittest.main()
