import unittest
import canopen.objectdictionary


class DatatypesTest(unittest.TestCase):
	def testName(self):
		with self.subTest("datatype=BOOLEAN"):
			self.assertEqual(canopen.objectdictionary.datatypes.BOOLEAN, 0x01)
		
		with self.subTest("datatype=INTEGER8"):
			self.assertEqual(canopen.objectdictionary.datatypes.INTEGER8, 0x02)
		
		with self.subTest("datatype=INTEGER16"):
			self.assertEqual(canopen.objectdictionary.datatypes.INTEGER16, 0x03)
		
		with self.subTest("datatype=INTEGER32"):
			self.assertEqual(canopen.objectdictionary.datatypes.INTEGER32, 0x04)
		
		with self.subTest("datatype=UNSIGNED8"):
			self.assertEqual(canopen.objectdictionary.datatypes.UNSIGNED8, 0x05)
		
		with self.subTest("datatype=UNSIGNED16"):
			self.assertEqual(canopen.objectdictionary.datatypes.UNSIGNED16, 0x06)
		
		with self.subTest("datatype=UNSIGNED32"):
			self.assertEqual(canopen.objectdictionary.datatypes.UNSIGNED32, 0x07)
		
		with self.subTest("datatype=REAL32"):
			self.assertEqual(canopen.objectdictionary.datatypes.REAL32, 0x08)
		
		with self.subTest("datatype=VISIBLE_STRING"):
			self.assertEqual(canopen.objectdictionary.datatypes.VISIBLE_STRING, 0x09)
		
		with self.subTest("datatype=OCTET_STRING"):
			self.assertEqual(canopen.objectdictionary.datatypes.OCTET_STRING, 0x0A)
		
		with self.subTest("datatype=UNICODE_STRING"):
			self.assertEqual(canopen.objectdictionary.datatypes.UNICODE_STRING, 0x0B)
		
		with self.subTest("datatype=TIME_OF_DAY"):
			self.assertEqual(canopen.objectdictionary.datatypes.TIME_OF_DAY, 0x0C)
		
		with self.subTest("datatype=TIME_DIFFERENCE"):
			self.assertEqual(canopen.objectdictionary.datatypes.TIME_DIFFERENCE, 0x0D)
		
		with self.subTest("datatype=DOMAIN"):
			self.assertEqual(canopen.objectdictionary.datatypes.DOMAIN, 0x0F)
		
		with self.subTest("datatype=INTEGER24"):
			self.assertEqual(canopen.objectdictionary.datatypes.INTEGER24, 0x10)
		
		with self.subTest("datatype=REAL64"):
			self.assertEqual(canopen.objectdictionary.datatypes.REAL64, 0x11)
		
		with self.subTest("datatype=INTEGER40"):
			self.assertEqual(canopen.objectdictionary.datatypes.INTEGER40, 0x12)
		
		with self.subTest("datatype=INTEGER48"):
			self.assertEqual(canopen.objectdictionary.datatypes.INTEGER48, 0x13)
		
		with self.subTest("datatype=INTEGER56"):
			self.assertEqual(canopen.objectdictionary.datatypes.INTEGER56, 0x14)
		
		with self.subTest("datatype=INTEGER64"):
			self.assertEqual(canopen.objectdictionary.datatypes.INTEGER64, 0x15)
		
		with self.subTest("datatype=UNSIGNED24"):
			self.assertEqual(canopen.objectdictionary.datatypes.UNSIGNED24, 0x16)
		
		with self.subTest("datatype=UNSIGNED40"):
			self.assertEqual(canopen.objectdictionary.datatypes.UNSIGNED40, 0x18)
		
		with self.subTest("datatype=UNSIGNED48"):
			self.assertEqual(canopen.objectdictionary.datatypes.UNSIGNED48, 0x19)
		
		with self.subTest("datatype=UNSIGNED56"):
			self.assertEqual(canopen.objectdictionary.datatypes.UNSIGNED56, 0x1A)
		
		with self.subTest("datatype=UNSIGNED64"):
			self.assertEqual(canopen.objectdictionary.datatypes.UNSIGNED64, 0x1B)


if __name__ == "__main__":
	unittest.main()
