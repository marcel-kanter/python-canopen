import unittest
import canopen.objectdictionary


class DefTypeTestCase(unittest.TestCase):
	def test_init(self):
		with self.assertRaises(ValueError):
			canopen.objectdictionary.DefType("deftype", -1)
		with self.assertRaises(ValueError):
			canopen.objectdictionary.DefType("deftype", 65536)
		
		name = "deftype"
		index = 100
		deftype = canopen.objectdictionary.DefType(name, index)
		
		self.assertEqual(deftype.name, name)
		self.assertEqual(deftype.index, index)
		self.assertEqual(deftype.subindex, 0)
		self.assertEqual(deftype.data_type, canopen.objectdictionary.UNSIGNED32)
		self.assertEqual(deftype.access_type, "ro")
		
		with self.assertRaises(AttributeError):
			deftype.name = name
		with self.assertRaises(AttributeError):
			deftype.index = index
		with self.assertRaises(AttributeError):
			deftype.subindex = 0
		with self.assertRaises(AttributeError):
			deftype.data_type = canopen.objectdictionary.UNSIGNED32
		with self.assertRaises(AttributeError):
			deftype.access_type = "ro"


if __name__ == "__main__":
	unittest.main()
