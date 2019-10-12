import unittest
import canopen.node.service


class ServiceTestCase(unittest.TestCase):
	def test_init(self):
		canopen.node.service.Service()
	
	def test_attach_detach(self):
		network = canopen.Network()
		dictionary = canopen.ObjectDictionary()
		node1 = canopen.Node("a", 1, dictionary)
		node2 = canopen.Node("b", 2, dictionary)
		examinee = canopen.node.service.Service()
		
		node1.attach(network)
		node2.attach(network)
		
		self.assertEqual(examinee.node, None)
		
		with self.assertRaises(RuntimeError):
			examinee.detach()
		
		with self.assertRaises(TypeError):
			examinee.attach(None)
		
		self.assertFalse(examinee.is_attached())
		
		examinee.attach(node1)
		self.assertTrue(examinee.is_attached())
		self.assertEqual(examinee.node, node1)
		
		with self.assertRaises(ValueError):
			examinee.attach(node1)
		
		examinee.attach(node2)
		self.assertTrue(examinee.is_attached())
		self.assertEqual(examinee.node, node2)
		
		examinee.detach()
		self.assertFalse(examinee.is_attached())
		self.assertEqual(examinee.node, None)
		
		node1.detach()
		node2.detach()


if __name__ == "__main__":
	unittest.main()
