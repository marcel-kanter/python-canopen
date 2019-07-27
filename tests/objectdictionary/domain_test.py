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
		examinee = canopen.objectdictionary.Domain(name, index, access_type)
		
		self.assertEqual(examinee.object_type, 2)
		self.assertEqual(examinee.name, name)
		self.assertEqual(examinee.index, index)
		self.assertEqual(examinee.subindex, 0)
		self.assertEqual(examinee.data_type, canopen.objectdictionary.DOMAIN)
		self.assertEqual(examinee.access_type, access_type)
		
		with self.assertRaises(AttributeError):
			examinee.name = name
		with self.assertRaises(AttributeError):
			examinee.index = index
		with self.assertRaises(AttributeError):
			examinee.subindex = 0
		with self.assertRaises(AttributeError):
			examinee.data_type = canopen.objectdictionary.DOMAIN


if __name__ == "__main__":
	unittest.main()
