import unittest
import can
import canopen.node.service.srdo


class SRDOProducerTestCase(unittest.TestCase):
	def test_init(self):
		canopen.node.service.srdo.SRDOProducer()
	
	def test_attach_detach(self):
		dictionary = canopen.ObjectDictionary()
		network = canopen.Network()
		node1 = canopen.Node("a", 1, dictionary)
		node2 = canopen.Node("b", 2, dictionary)
		examinee = canopen.node.service.srdo.SRDOProducer()
		
		node1.attach(network)
		node2.attach(network)
		
		self.assertEqual(examinee.node, None)
		
		with self.assertRaises(RuntimeError):
			examinee.detach()
		
		with self.assertRaises(TypeError):
			examinee.attach(None)
		
		test_data = [-1, 0x100000000]
		for value in test_data:
			with self.subTest(value = value):
				with self.assertRaises(ValueError):
					examinee.attach(node1, value, 0)
				with self.assertRaises(ValueError):
					examinee.attach(node1, 0, value)
		
		examinee.attach(node1)
		self.assertEqual(examinee.node, node1)
		
		with self.assertRaises(ValueError):
			examinee.attach(node1)
		
		examinee.attach(node2, (1 << 29) | 0x80)
		self.assertEqual(examinee.node, node2)
		
		examinee.detach()
		self.assertEqual(examinee.node, None)
		
		node1.detach()
		node2.detach()
	
	def test_send(self):
		bus1 = can.Bus(interface = "virtual", channel = 0)
		bus2 = can.Bus(interface = "virtual", channel = 0)
		network = canopen.Network()
		dictionary = canopen.ObjectDictionary()
		node = canopen.Node("a", 1, dictionary)
		examinee = canopen.node.service.srdo.SRDOProducer()
		
		network.attach(bus1)
		node.attach(network)
		examinee.attach(node)
		
		
		
		examinee.detach()
		node.detach()
		network.detach()
		bus1.shutdown()
		bus2.shutdown()
