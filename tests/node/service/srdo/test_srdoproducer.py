import unittest
import can
import canopen.node.service.srdo

from canopen import Node, Network
from canopen.objectdictionary import ObjectDictionary
from canopen.node.service.srdo import SRDOProducer


class SRDOProducerTestCase(unittest.TestCase):
	def test_init(self):
		dictionary = ObjectDictionary()
		node = Node("n", 1, dictionary)
		examinee = SRDOProducer(node)
		
		self.assertEqual(examinee.node, node)
		
		test_data = [b"\x22", None, b"\x11\x00"]
		for value in test_data:
			with self.subTest("value = " + str(value)):
				examinee.normal_data = value
				self.assertEqual(examinee.normal_data, value)
				examinee.complement_data = value
				self.assertEqual(examinee.complement_data, value)
	
	def test_attach_detach(self):
		dictionary = ObjectDictionary()
		node = Node("n", 1, dictionary)
		examinee = SRDOProducer(node)
		network = Network()
		
		node.attach(network)
		
		with self.assertRaises(RuntimeError):
			examinee.detach()
		
		test_data = [-1, 0x100000000]
		for value in test_data:
			with self.subTest(value = value):
				with self.assertRaises(ValueError):
					examinee.attach(value, 0)
				with self.assertRaises(ValueError):
					examinee.attach(0, value)
		
		examinee.attach()
		self.assertTrue(examinee.is_attached())
		
		examinee.attach((1 << 29) | 0xFF + 2 * node.id, (1 << 29) | 0x100 + 2 * node.id)
		self.assertTrue(examinee.is_attached())
		
		examinee.detach()
		self.assertFalse(examinee.is_attached())
		
		node.detach()
	
	def test_send(self):
		bus1 = can.Bus(interface = "virtual", channel = 0)
		bus2 = can.Bus(interface = "virtual", channel = 0)
		dictionary = ObjectDictionary()
		node = Node("a", 1, dictionary)
		examinee = SRDOProducer(node)
		network = Network()
		
		network.attach(bus1)
		node.attach(network)
		examinee.attach()
		
		examinee.data = None
		with self.assertRaises(RuntimeError):
			examinee.send()
		
		cob_ids = [(0x101, 0x102), ((1 << 29) | 0x101, (1 << 29) | 0x102)]
		for cob_id_1, cob_id_2 in cob_ids:
			normal_data = b"\xAA"
			complement_data = b"\x55"
			
			examinee.attach(cob_id_1, cob_id_2)
			
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
