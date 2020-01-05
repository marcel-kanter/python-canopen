import unittest
import canopen.objectdictionary
from canopen.node.service.objectmapping import ObjectMapping


class ObjectMappingTest(unittest.TestCase):
	def test_init(self):
		examinee = ObjectMapping()
		self.assertEqual(len(examinee), 0)
	
	def test_list(self):
		d = canopen.ObjectDictionary()
		d.add(canopen.objectdictionary.Variable("var", 0x2000, 0x00, canopen.objectdictionary.INTEGER32))
		
		examinee = ObjectMapping()
		
		with self.assertRaises(ValueError):
			examinee.append((0x1000, 0x00), -1)
		
		with self.assertRaises(IndexError):
			examinee[0]
		
		examinee.append((0x1000, 0x00), 0)
		self.assertEqual(len(examinee), 1)
		self.assertEqual(examinee[0], ((0x1000, 0x00), 0))
		
		examinee.append((0x1000, 0x00), 1)
		self.assertEqual(len(examinee), 2)
		self.assertEqual(examinee[1], ((0x1000, 0x00), 1))
		
		examinee.append(d["var"], 10)
		self.assertEqual(len(examinee), 3)
		self.assertEqual(examinee[2], (d["var"], 10))
		
		examinee.clear()
		self.assertEqual(len(examinee), 0)
		with self.assertRaises(IndexError):
			examinee[0]
		with self.assertRaises(IndexError):
			examinee[1]
		with self.assertRaises(IndexError):
			examinee[2]


if __name__ == "__main__":
	unittest.main()
