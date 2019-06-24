import unittest
import time
import struct
import can
import canopen.node.service.sync


class SYNCProducerTestCase(unittest.TestCase):
	def test_init(self):
		canopen.node.service.sync.SYNCProducer()
	
	def test_attach_detach(self):
		dictionary = canopen.ObjectDictionary()
		network = canopen.Network()
		node1 = canopen.Node("a", 1, dictionary)
		node2 = canopen.Node("b", 2, dictionary)
		examinee = canopen.node.service.sync.SYNCProducer()
		
		node1.attach(network)
		node2.attach(network)
		
		self.assertEqual(examinee.node, None)
		
		with self.assertRaises(RuntimeError):
			examinee.detach()
		
		with self.assertRaises(TypeError):
			examinee.attach(None)
		
		examinee.attach(node1)
		self.assertEqual(examinee.node, node1)
		
		with self.assertRaises(ValueError):
			examinee.attach(node1)
		
		examinee.attach(node2)
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
		examinee = canopen.node.service.sync.SYNCProducer()
		
		network.attach(bus1)
		node.attach(network)
		examinee.attach(node)
		
		#### Test step: Legacy sync message without counter
		value = None
		examinee.send(value)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x80)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.dlc, 0)
		
		#### Test step: sync message with counter
		value = 111
		examinee.send(value)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x80)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<B", value))
		
		examinee.detach()
		node.detach()
		network.detach()
		bus1.shutdown()
		bus2.shutdown()
	