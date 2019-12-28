import unittest
from unittest.mock import Mock
import time
import can
import canopen.node.service.srdo


class SRDOConsumerTestCase(unittest.TestCase):
	def test_init(self):
		examinee = canopen.node.service.srdo.SRDOConsumer()
		
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
		
		self.assertEqual(examinee.normal_data, b"\x00")
		
		message = can.Message(arbitration_id =  0x100 + 2 * node.id, is_extended_id = False, is_remote_frame = False, data = b"\xFF")
		bus2.send(message)
		time.sleep(0.01)
		
		self.assertEqual(examinee.complement_data, b"\xFF")
		
		#### Test step: Ignore RTR
		message = can.Message(arbitration_id = 0xFF + 2 * node.id, is_extended_id = False, is_remote_frame = True, dlc = 1)
		bus2.send(message)
		time.sleep(0.01)
		
		self.assertEqual(examinee.normal_data, b"\x00")
		
		message = can.Message(arbitration_id =  0x100 + 2 * node.id, is_extended_id = False, is_remote_frame = True, dlc = 1)
		bus2.send(message)
		time.sleep(0.01)
		
		self.assertEqual(examinee.complement_data, b"\xFF")
		
		#### Test step: Ignore wrong frame type
		message = can.Message(arbitration_id = 0xFF + 2 * node.id, is_extended_id = True, is_remote_frame = False, data = b"\x00")
		bus2.send(message)
		time.sleep(0.01)
		
		self.assertEqual(examinee.normal_data, b"\x00")
		
		message = can.Message(arbitration_id =  0x100 + 2 * node.id, is_extended_id = True, is_remote_frame = False, data = b"\xFF")
		bus2.send(message)
		time.sleep(0.01)
		
		self.assertEqual(examinee.complement_data, b"\xFF")
		
		#### Test step: Correct frame pair, service just collects
		message = can.Message(arbitration_id = 0xFF + 2 * node.id, is_extended_id = False, is_remote_frame = False, data = b"\xAA")
		bus2.send(message)
		time.sleep(0.01)
		
		self.assertEqual(examinee.normal_data, b"\xAA")
		
		message = can.Message(arbitration_id =  0x100 + 2 * node.id, is_extended_id = False, is_remote_frame = False, data = b"\xCC")
		bus2.send(message)
		time.sleep(0.01)
		
		self.assertEqual(examinee.complement_data, b"\xCC")
		
		examinee.detach()
		node.detach()
		network.detach()
		bus1.shutdown()
		bus2.shutdown()
	
	def test_sync(self):
		bus1 = can.Bus(interface = "virtual", channel = 0)
		bus2 = can.Bus(interface = "virtual", channel = 0)
		network = canopen.Network()
		dictionary = canopen.ObjectDictionary()
		node = canopen.Node("a", 1, dictionary)
		examinee = canopen.node.service.srdo.SRDOConsumer()
		
		cb1 = Mock()
		examinee.add_callback("sync", cb1)
		
		network.attach(bus1)
		node.attach(network)
		examinee.attach(node)
		
		#### Test step: Sync message
		test_data = [(None, None), (b"", None), (b"\x01", 1)]
		for data, counter in test_data:
			with self.subTest("sync message", data = data):
				cb1.reset_mock()
				message = can.Message(arbitration_id = 0x80, is_extended_id = False, data = data)
				bus2.send(message)
				time.sleep(0.001)
				cb1.assert_called_with("sync", examinee, counter)
		
		#### Test step: sync message, ignore remote frame
		cb1.reset_mock()
		message = can.Message(arbitration_id = 0x80, is_extended_id = True, data = b"\x01")
		bus2.send(message)
		time.sleep(0.001)
		cb1.assert_not_called()
		
		#### Test step: sync message, ignore remote frame
		cb1.reset_mock()
		message = can.Message(arbitration_id = 0x80, is_extended_id = False, is_remote_frame = True, dlc = 1)
		bus2.send(message)
		time.sleep(0.001)
		cb1.assert_not_called()
		
		examinee.detach()
		node.detach()
		network.detach()
		bus1.shutdown()
		bus2.shutdown()
