import unittest
import canopen.node.service.objectmapping
import canopen.objectdictionary.variable


class ObjectMappingTest(unittest.TestCase):
	def test_init(self):
		examinee = canopen.node.service.objectmapping.ObjectMapping()
	
	def test_equals(self):
		a = canopen.node.service.objectmapping.ObjectMapping()
		
		#### Test step: Reflexivity
		self.assertTrue(a == a)
		
		#### Test step: Compare same classes only (required for transitivity)
		test_data = [None, 3]
		for value in test_data:
			with self.subTest("value=" + str(value)):
				self.assertFalse(a == value)
		
		#### Test step: Consistency
		b = canopen.node.service.objectmapping.ObjectMapping()
		for _ in range(3):
			self.assertTrue(a == b)
		
		#### Test step: Symmetricality, Contents
		b = canopen.node.service.objectmapping.ObjectMapping()
		self.assertTrue(a == b)
		self.assertEqual(a == b, b == a)
		
		x = object()
		b.append(x)
		self.assertFalse(a == b)
		self.assertEqual(a == b, b == a)
		
		a.append(x)
		self.assertTrue(a == b)
		self.assertEqual(a == b, b == a)
		
		b.append(x)
		self.assertFalse(a == b)
		self.assertEqual(a == b, b == a)
	
	def test_list(self):
		examinee = canopen.node.service.objectmapping.ObjectMapping()
		
		self.assertEqual(len(examinee), 0)
		
		a = canopen.objectdictionary.Variable("a", 0x01, 0x00, canopen.objectdictionary.UNSIGNED32)
		b = canopen.objectdictionary.Variable("b", 0x02, 0x00, canopen.objectdictionary.UNSIGNED32)
		
		examinee.append(a)
		self.assertEqual(len(examinee), 1)
		self.assertTrue(a in examinee)
		
		examinee.insert(0, b)
		self.assertEqual(len(examinee), 2)
		self.assertTrue(b in examinee)
		
		items = []
		for i in examinee:
			items.append(i)
		
		self.assertEqual(items[0], b)
		self.assertEqual(items[1], a)
		
		examinee.remove(b)
		self.assertEqual(len(examinee), 1)
		self.assertTrue(a in examinee)
		self.assertFalse(b in examinee)
		
		examinee.clear()
		self.assertEqual(len(examinee), 0)
		self.assertFalse(a in examinee)
		self.assertFalse(b in examinee)
