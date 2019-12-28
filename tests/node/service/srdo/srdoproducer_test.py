import unittest
import can
import canopen.node.service.srdo


class SRDOProducerTestCase(unittest.TestCase):
	def test_init(self):
		examinee = canopen.node.service.srdo.SRDOProducer()
		
		test_data = [b"\x22", None, b"\x11\x00"]
		for value in test_data:
			with self.subTest("value = " + str(value)):
				examinee.normal_data = value
				self.assertEqual(examinee.normal_data, value)
				examinee.complement_data = value
				self.assertEqual(examinee.complement_data, value)
	
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
		
		examinee.data = None
		with self.assertRaises(RuntimeError):
			examinee.send()
		
		cob_ids = [(0x101, 0x102), ((1 << 29) | 0x101, (1 << 29) | 0x102)]
		for cob_id_1, cob_id_2 in cob_ids:
			normal_data = b"\xAA"
			complement_data = b"\x55"
			
			examinee.attach(node, cob_id_1, cob_id_2)
			
			with self.subTest("cub_id_1=" + hex(cob_id_1) + ", cob_id_2=" + hex(cob_id_2)):
				examinee.normal_data = normal_data
				examinee.complement_data = complement_data
				examinee.send()
				
				message = bus2.recv(0.1)
				self.assertEqual(message.arbitration_id, cob_id_1 & 0x1FFFFFFF)
				self.assertEqual(message.is_extended_id, bool(cob_id_1 & (1 << 29)))
				self.assertEqual(message.data, normal_data)
				
				message = bus2.recv(0.1)
				self.assertEqual(message.arbitration_id, cob_id_2 & 0x1FFFFFFF)
				self.assertEqual(message.is_extended_id, bool(cob_id_1 & (1 << 29)))
				self.assertEqual(message.data, complement_data)
			
			examinee.detach()
		
		node.detach()
		network.detach()
		bus1.shutdown()
		bus2.shutdown()
