import unittest
import canopen.objectdictionary


class VariableTestCase(unittest.TestCase):
	def test_init(self):
		with self.assertRaises(ValueError):
			canopen.objectdictionary.Variable("var", -1, 0, canopen.objectdictionary.UNSIGNED32)
		with self.assertRaises(ValueError):
			canopen.objectdictionary.Variable("var", 65536, 0, canopen.objectdictionary.UNSIGNED32)
		with self.assertRaises(ValueError):
			canopen.objectdictionary.Variable("var", 0, -1, canopen.objectdictionary.UNSIGNED32)
		with self.assertRaises(ValueError):
			canopen.objectdictionary.Variable("var", 0, 256, canopen.objectdictionary.UNSIGNED32)
		
		name = "var"
		index = 100
		subindex = 0
		data_type = canopen.objectdictionary.UNSIGNED32
		variable = canopen.objectdictionary.Variable(name, index, subindex, data_type)
		
		self.assertEqual(variable.name, name)
		self.assertEqual(variable.index, index)
		self.assertEqual(variable.subindex, subindex)
		self.assertEqual(variable.data_type, data_type)
		
		with self.assertRaises(AttributeError):
			variable.name = name
		with self.assertRaises(AttributeError):
			variable.index = index
		with self.assertRaises(AttributeError):
			variable.subindex = subindex
		with self.assertRaises(AttributeError):
			variable.data_type = data_type


if __name__ == "__main__":
	unittest.main()
