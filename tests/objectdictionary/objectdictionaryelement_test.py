import unittest
import canopen.objectdictionary


class ObjectDictionaryElementTest(unittest.TestCase):
	def test_init(self):
		with self.assertRaises(ValueError):
			canopen.objectdictionary.ObjectDictionaryElement("var", -1)
		with self.assertRaises(ValueError):
			canopen.objectdictionary.ObjectDictionaryElement("var", 65536)
		
		examinee = canopen.objectdictionary.ObjectDictionaryElement("a", 1)
		
		desc = "Franz jagt im komplett verwahrlosten Taxi quer durch Bayern."
		examinee.description = desc
		self.assertEqual(examinee.description, desc)
	
	def test_equals(self):
		a = canopen.objectdictionary.ObjectDictionaryElement("a", 1)
		
		#### Test step: Reflexivity
		self.assertTrue(a == a)
		
		#### Test step: Compare same classes only (required for transitivity)
		test_data = [None, 3]
		for value in test_data:
			with self.subTest("value=" + str(value)):
				self.assertFalse(a == value)
		
		#### Test step: Consistency
		b = canopen.objectdictionary.ObjectDictionaryElement("a", 1)
		for _ in range(3):
			self.assertTrue(a == b)
		
		#### Test step: Symmetricality, Contents
		b = canopen.objectdictionary.ObjectDictionaryElement("b", 1)
		self.assertFalse(a == b)
		self.assertEqual(a == b, b == a)
		
		b = canopen.objectdictionary.ObjectDictionaryElement("a", 2)
		self.assertFalse(a == b)
		self.assertEqual(a == b, b == a)


if __name__ == "__main__":
	unittest.main()
