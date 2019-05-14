import unittest
import canopen


class VariableTestCase(unittest.TestCase):
	def test_init(self):
		with self.assertRaises(ValueError):
			variable = canopen.objectdictionary.Variable("var", -1, 0)
		with self.assertRaises(ValueError):
			variable = canopen.objectdictionary.Variable("var", 65536, 0)
		with self.assertRaises(ValueError):
			variable = canopen.objectdictionary.Variable("var", 0, -1)
		with self.assertRaises(ValueError):
			variable = canopen.objectdictionary.Variable("var", 0, 256)
		
		name = "var"
		index = 100
		subindex = 0
		variable = canopen.objectdictionary.Variable(name, index, subindex)
		
		self.assertEqual(variable.name, name)
		self.assertEqual(variable.index, index)
		self.assertEqual(variable.subindex, subindex)
		
		with self.assertRaises(AttributeError):
			variable.name = name
		with self.assertRaises(AttributeError):
			variable.index = index
		with self.assertRaises(AttributeError):
			variable.subindex = subindex


if __name__ == "__main__":
	unittest.main()
