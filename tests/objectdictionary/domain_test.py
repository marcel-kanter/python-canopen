import unittest
import canopen.objectdictionary


class DomainTest(unittest.TestCase):
	def test_init(self):
		with self.assertRaises(ValueError):
			canopen.objectdictionary.Domain("domain", -1)
		with self.assertRaises(ValueError):
			canopen.objectdictionary.Domain("domain", 65536)
		
		name = "domain"
		index = 100
		access_type = "rw"
		deftype = canopen.objectdictionary.Domain(name, index, access_type)
		
		self.assertEqual(deftype.name, name)
		self.assertEqual(deftype.index, index)
		self.assertEqual(deftype.subindex, 0)
		self.assertEqual(deftype.data_type, canopen.objectdictionary.DOMAIN)
		self.assertEqual(deftype.access_type, access_type)
		
		with self.assertRaises(AttributeError):
			deftype.name = name
		with self.assertRaises(AttributeError):
			deftype.index = index
		with self.assertRaises(AttributeError):
			deftype.subindex = 0
		with self.assertRaises(AttributeError):
			deftype.data_type = canopen.objectdictionary.UNSIGNED32


if __name__ == "__main__":
	unittest.main()
