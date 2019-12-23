import unittest
import canopen.objectdictionary
import canopen.node

from tests.node.inspectionnode import InspectionNode


class VariableTestCase(unittest.TestCase):
	def test_init(self):
		dictionary = canopen.ObjectDictionary()
		node = InspectionNode("n", 1, dictionary)
		entry = canopen.objectdictionary.Variable("unsigned32", 0x1234, 0x07, canopen.objectdictionary.UNSIGNED32, "rw")
		entry.description = "Tempus transit horridum frigus"
		
		with self.assertRaises(TypeError):
			canopen.node.variable.Variable(dictionary, entry)
		with self.assertRaises(TypeError):
			canopen.node.variable.Variable(node, node)
		
		examinee = canopen.node.variable.Variable(node, entry)
		
		#### Test step: property forwarding
		self.assertEqual(examinee.object_type, entry.object_type)
		self.assertEqual(examinee.name, entry.name)
		self.assertEqual(examinee.index, entry.index)
		self.assertEqual(examinee.subindex, entry.subindex)
		self.assertEqual(examinee.data_type, entry.data_type)
		self.assertEqual(examinee.access_type, entry.access_type)
		self.assertEqual(examinee.default_value, entry.default_value)
		self.assertEqual(examinee.description, entry.description)
		self.assertEqual(examinee.size, entry.size)
		
		#### Test step: data access set_data
		value = 100
		examinee.value = value
		node.set_data.assert_called_with(entry.index, entry.subindex, value)
		
		#### Test step: data access get_data
		self.assertEqual(examinee.value, value)
		node.get_data.assert_called_with(entry.index, entry.subindex)


if __name__ == "__main__":
	unittest.main()
