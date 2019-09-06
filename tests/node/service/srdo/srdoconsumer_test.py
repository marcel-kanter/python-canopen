import unittest
import time
import can
import canopen.node.service.srdo


class SRDOConsumerTestCase(unittest.TestCase):
	def test_init(self):
		canopen.node.service.srdo.SRDOConsumer()
	
	def test_attach_detach(self):
		dictionary = canopen.ObjectDictionary()
		network = canopen.Network()
		node1 = canopen.Node("a", 1, dictionary)
		node2 = canopen.Node("b", 2, dictionary)
		examinee = canopen.node.service.srdo.SRDOConsumer()
		
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
		
		examinee.attach(node2, (1 << 29) | 0xFF + 2 * node2.id, (1 << 29) | 0x100 + 2 * node2.id)
		self.assertEqual(examinee.node, node2)
		
		examinee.detach()
		self.assertEqual(examinee.node, None)
		
		node1.detach()
		node2.detach()
	
	def test_on_message(self):
		bus1 = can.Bus(interface = "virtual", channel = 0)
		bus2 = can.Bus(interface = "virtual", channel = 0)
		network = canopen.Network()
		dictionary = canopen.ObjectDictionary()
		node = canopen.Node("a", 1, dictionary)
		examinee = canopen.node.service.srdo.SRDOConsumer()
		
		network.attach(bus1)
		node.attach(network)
		examinee.attach(node)
		
		#### Test step: Correct frame pair
		message = can.Message(arbitration_id = 0xFF + 2 * node.id, is_extended_id = False, is_remote_frame = False, data = b"\x00")
		bus2.send(message)
		time.sleep(0.01)
		
		message = can.Message(arbitration_id =  0x100 + 2 * node.id, is_extended_id = False, is_remote_frame = False, data = b"\xFF")
		bus2.send(message)
		time.sleep(0.01)
		
		#### Test step: Ignore RTR
		message = can.Message(arbitration_id = 0xFF + 2 * node.id, is_extended_id = False, is_remote_frame = True, dlc = 1)
		bus2.send(message)
		time.sleep(0.01)
		
		message = can.Message(arbitration_id =  0x100 + 2 * node.id, is_extended_id = False, is_remote_frame = True, dlc = 1)
		bus2.send(message)
		time.sleep(0.01)
		
		#### Test step: Ignore wrong frame type
		message = can.Message(arbitration_id = 0xFF + 2 * node.id, is_extended_id = True, is_remote_frame = False, data = b"\x00")
		bus2.send(message)
		time.sleep(0.01)
		
		message = can.Message(arbitration_id =  0x100 + 2 * node.id, is_extended_id = True, is_remote_frame = False, data = b"\xFF")
		bus2.send(message)
		time.sleep(0.01)
		
		examinee.detach()
		node.detach()
		network.detach()
		bus1.shutdown()
		bus2.shutdown()
