import unittest

import canopen.objectdictionary
from canopen.node.service import Service
from canopen.node.service.objectmapping import ObjectMapping
from canopen.node.node import Node


class ObjectMappingTest(unittest.TestCase):
	def test_init(self):
		dictionary = canopen.ObjectDictionary()
		dictionary.add(canopen.objectdictionary.Variable("var", 0x2000, 0x00, canopen.objectdictionary.INTEGER32))
		node = Node("a", 1, dictionary)
		service = Service(node)
		examinee = ObjectMapping(service)
		self.assertEqual(len(examinee), 0)
		self.assertEqual(examinee.size, 0)
	
		with self.assertRaises(TypeError):
			ObjectMapping(None)
	
	def test_list(self):
		dictionary = canopen.ObjectDictionary()
		dictionary.add(canopen.objectdictionary.Variable("var", 0x2000, 0x00, canopen.objectdictionary.INTEGER32))
		node = Node("a", 1, dictionary)
		service = Service(node)
		examinee = ObjectMapping(service)
		
		with self.assertRaises(ValueError):
			examinee.append((0x1000, 0x00), -1)
		
		with self.assertRaises(IndexError):
			examinee[0]
		
		examinee.append((0x1000, 0x00), 20)
		self.assertEqual(len(examinee), 1)
		self.assertEqual(examinee.size, 20)
		mapped_variable = examinee[0]
		self.assertEqual(mapped_variable.index, 0x1000)
		self.assertEqual(mapped_variable.subindex, 0x00)
		self.assertEqual(mapped_variable.size, 20)
		
		examinee.append((0x1000, 0x00), 1)
		self.assertEqual(examinee.size, 21)
		self.assertEqual(len(examinee), 2)
		mapped_variable = examinee[1]
		self.assertEqual(mapped_variable.index, 0x1000)
		self.assertEqual(mapped_variable.subindex, 0x00)
		self.assertEqual(mapped_variable.size, 1)
		
		examinee.append(dictionary["var"], 10)
		self.assertEqual(examinee.size, 31)
		self.assertEqual(len(examinee), 3)
		mapped_variable = examinee[2]
		self.assertEqual(mapped_variable.index, dictionary["var"].index)
		self.assertEqual(mapped_variable.subindex, dictionary["var"].subindex)
		self.assertEqual(mapped_variable.size, 10)
		
		examinee.clear()
		self.assertEqual(len(examinee), 0)
		self.assertEqual(examinee.size, 0)
		with self.assertRaises(IndexError):
			examinee[0]
		with self.assertRaises(IndexError):
			examinee[1]
		with self.assertRaises(IndexError):
			examinee[2]


if __name__ == "__main__":
	unittest.main()
