import unittest
from unittest.mock import Mock
from canopen import Node
from canopen.objectdictionary import ObjectDictionary
from canopen.node.service import Service


class ServiceTestCase(unittest.TestCase):
	def test_init(self):
		dictionary = ObjectDictionary()
		node = Node("n", 1, dictionary)
		examinee = Service(node)
		
		self.assertEqual(examinee.node, node)
		
		with self.assertRaises(TypeError):
			node = None
			Service(node)
	
	def test_attach_detach(self):
		dictionary = ObjectDictionary()
		node = Node("n", 1, dictionary)
		examinee = Service(node)
		
		with self.assertRaises(NotImplementedError):
			examinee.attach()
		
		with self.assertRaises(NotImplementedError):
			examinee.detach()
		
		with self.assertRaises(NotImplementedError):
			examinee.is_attached()
	
	def test_callback(self):
		dictionary = ObjectDictionary()
		node = Node("n", 1, dictionary)
		examinee = Service(node)
		
		callback = Mock(side_effect = Exception)
		
		# The base class does not contain events by default
		event = "ABC"
		with self.assertRaises(TypeError):
			examinee.add_callback(event, None)
		
		with self.assertRaises(KeyError):
			examinee.add_callback(event, callback)
		
		examinee.add_event(event)
		examinee.add_callback(event, callback)
		
		with self.assertRaises(KeyError):
			examinee.add_event(event)
		
		with self.assertRaises(KeyError):
			examinee.notify("XYZ")
		
		examinee.notify(event)
		callback.assert_called_once_with(event)
		
		with self.assertRaises(KeyError):
			examinee.remove_callback("XYZ", callback)
		with self.assertRaises(ValueError):
			examinee.remove_callback(event, None)
			
		examinee.remove_callback(event, callback)
		with self.assertRaises(ValueError):
			examinee.remove_callback(event, callback)
		
		with self.assertRaises(KeyError):
			examinee.remove_event("XYZ")
		
		examinee.remove_event(event)
		
		with self.assertRaises(KeyError):
			examinee.remove_event(event)


if __name__ == "__main__":
	unittest.main()
