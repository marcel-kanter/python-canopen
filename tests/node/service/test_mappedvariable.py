import unittest
import canopen.objectdictionary
from canopen.node.service import Service
from canopen.node.service.objectmapping import ObjectMapping
from canopen.node.service.mappedvariable import MappedVariable
from canopen.node.node import Node


class MappedVariableTest(unittest.TestCase):
	def test_init(self):
		dictionary = canopen.ObjectDictionary()
		dictionary.add(canopen.objectdictionary.Variable("var", 0x2000, 0x00, canopen.objectdictionary.INTEGER32))
		node = Node("a", 1, dictionary)
		service = Service(node)
		mapping = ObjectMapping(service)
		
		with self.subTest("tuple"):
			slot = 0
			index = 0x1000
			subindex = 0x00
			size = 10
			
			entry = (index, subindex)
			examinee = MappedVariable(mapping, slot, entry, size)
			
			self.assertEqual(examinee.index, index)
			self.assertEqual(examinee.subindex, subindex)
			self.assertEqual(examinee.size, size)
		
		with self.subTest("variable"):
			slot = 0
			entry = dictionary["var"]
			size = 15
			examinee = MappedVariable(mapping, slot, entry, size)
			
			self.assertEqual(examinee.index, entry.index)
			self.assertEqual(examinee.subindex, entry.subindex)
			self.assertEqual(examinee.size, size)


if __name__ == "__main__":
	unittest.main()
