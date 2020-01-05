import unittest
import canopen.objectdictionary
from canopen.node.service.objectmapping import ObjectMapping
from canopen.node.service.mappedvariable import MappedVariable


class MappedVariableTest(unittest.TestCase):
	def test_init(self):
		dictionary = canopen.ObjectDictionary()
		dictionary.add(canopen.objectdictionary.Variable("var", 0x2000, 0x00, canopen.objectdictionary.INTEGER32))
		mapping = ObjectMapping()
		
		with self.subTest("tuple"):
			slot = 0
			index = 0x1000
			subindex = 0x00
			
			entry = (index, subindex)
			examinee = MappedVariable(mapping, slot, entry)
			
			self.assertEqual(examinee.index, index)
			self.assertEqual(examinee.subindex, subindex)
		
		with self.subTest("variable"):
			slot = 0
			entry = dictionary["var"]
			examinee = MappedVariable(mapping, slot, entry)
			
			self.assertEqual(examinee.index, entry.index)
			self.assertEqual(examinee.subindex, entry.subindex)


if __name__ == "__main__":
	unittest.main()
