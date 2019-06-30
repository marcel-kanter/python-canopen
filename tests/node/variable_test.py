import unittest
from unittest.mock import Mock
import canopen.objectdictionary
import canopen.node


class InspectionNode(canopen.Node):
	def __init__(self, name, node_id, dictionary):
		canopen.Node.__init__(self, name, node_id, dictionary)
		self._data = {}
		self.get_data = Mock(side_effect = self._sideeffect_get_data)
		self.set_data = Mock(side_effect = self._sideeffect_set_data)
	
	def _sideeffect_get_data(self, index, subindex):
		return self._data[(index, subindex)]
	
	def _sideeffect_set_data(self, index, subindex, data):
		self._data[(index, subindex)] = data


class VariableTestCase(unittest.TestCase):
	def test_init(self):
		dictionary = canopen.ObjectDictionary()
		node = InspectionNode("n", 1, dictionary)
		entry = canopen.objectdictionary.Variable("unsigned32", 0x1234, 0x07, canopen.objectdictionary.UNSIGNED32, "rw")
		
		with self.assertRaises(TypeError):
			canopen.node.variable.Variable(dictionary, entry)
		with self.assertRaises(TypeError):
			canopen.node.variable.Variable(node, node)
		
		examinee = canopen.node.variable.Variable(node, entry)
		
		#### Test step: property forwarding
		self.assertEqual(examinee.name, entry.name)
		self.assertEqual(examinee.index, entry.index)
		self.assertEqual(examinee.subindex, entry.subindex)
		self.assertEqual(examinee.data_type, entry.data_type)
		self.assertEqual(examinee.access_type, entry.access_type)
		
		#### Test step: data access set_data
		value = 100
		examinee.value = value
		node.set_data.assert_called_with(entry.index, entry.subindex, value)
		
		#### Test step: data access get_data
		self.assertEqual(examinee.value, value)
		node.get_data.assert_called_with(entry.index, entry.subindex)


if __name__ == "__main__":
	unittest.main()
