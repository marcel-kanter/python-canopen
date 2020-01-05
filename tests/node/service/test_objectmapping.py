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
		
		examinee.append((0x1000, 0x00), 20)
		self.assertEqual(len(examinee), 1)
		variable, length = examinee[0]
		self.assertEqual(variable.index, 0x1000)
		self.assertEqual(variable.subindex, 0x00)
		self.assertEqual(length, 20)
		
		examinee.append((0x1000, 0x00), 1)
		self.assertEqual(len(examinee), 2)
		variable, length = examinee[1]
		self.assertEqual(variable.index, 0x1000)
		self.assertEqual(variable.subindex, 0x00)
		self.assertEqual(length, 1)
		
		examinee.append(d["var"], 10)
		self.assertEqual(len(examinee), 3)
		variable, length = examinee[2]
		self.assertEqual(variable.index, d["var"].index)
		self.assertEqual(variable.subindex, d["var"].subindex)
		self.assertEqual(length, 10)
		
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
