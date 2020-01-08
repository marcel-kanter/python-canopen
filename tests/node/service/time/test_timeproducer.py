import unittest
import calendar
import struct
import can

from canopen import Node, Network
from canopen.objectdictionary import ObjectDictionary
from canopen.node.service.time import TIMEProducer


class TIMEProducerTestCase(unittest.TestCase):
	def test_init(self):
		dictionary = ObjectDictionary()
		node = Node("n", 1, dictionary)
		examinee = TIMEProducer(node)
		
		self.assertEqual(examinee.node, node)
	
	def test_attach_detach(self):
		dictionary = ObjectDictionary()
		node = Node("n", 1, dictionary)
		examinee = TIMEProducer(node)
		network = Network()
		
		node.attach(network)
		
		with self.assertRaises(RuntimeError):
			examinee.detach()
		
		test_data = [-1, 0x100000000]
		for value in test_data:
			with self.subTest(value = value):
				with self.assertRaises(ValueError):
					examinee.attach(value)
		
		examinee.attach()
		self.assertTrue(examinee.is_attached())
		
		examinee.attach((1 << 29) | (0x100))
		self.assertTrue(examinee.is_attached())
		
		examinee.detach()
		self.assertFalse(examinee.is_attached())
		
		node.detach()
	
	def test_send(self):
		bus1 = can.Bus(interface = "virtual", channel = 0)
		bus2 = can.Bus(interface = "virtual", channel = 0)
		dictionary = ObjectDictionary()
		node = Node("a", 1, dictionary)
		examinee = TIMEProducer(node)
		network = Network()
		
		network.attach(bus1)
		node.attach(network)
		
		test_data = [0x100, (1 << 29) | 0x100]
		for cob_id in test_data:
			with self.subTest(cob_id = cob_id):
				examinee.attach(cob_id)
				
				#### Test step: Send CANopen epoch
				value = calendar.timegm((1984, 1, 1, 0, 0, 0))
				examinee.send(value)
				
				message_recv = bus2.recv(1)
				self.assertEqual(message_recv.arbitration_id, cob_id & 0x7FF)
				self.assertEqual(message_recv.is_extended_id, bool(cob_id & (1 << 29)))
				self.assertEqual(message_recv.data, struct.pack("<LH", 0, 0))
				
				#### Test step: Send 60 days after CANopen epoch (1984 is a leap year)
				value = calendar.timegm((1984, 3, 1, 0, 0, 0))
				examinee.send(value)
						
				message_recv = bus2.recv(1)
				self.assertEqual(message_recv.arbitration_id, cob_id & 0x7FF)
				self.assertEqual(message_recv.is_extended_id, bool(cob_id & (1 << 29)))
				self.assertEqual(message_recv.data, struct.pack("<LH", 0, 60))
				
				examinee.detach()
		
		node.detach()
		network.detach()
		bus1.shutdown()
		bus2.shutdown()
	