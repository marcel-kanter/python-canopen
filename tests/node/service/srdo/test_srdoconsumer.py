import unittest
from unittest.mock import Mock
import time
import can

from canopen import Node, Network
from canopen.objectdictionary import ObjectDictionary
from canopen.node.service.srdo import SRDOConsumer


class SRDOConsumerTestCase(unittest.TestCase):
	def test_init(self):
		dictionary = ObjectDictionary()
		node = Node("n", 1, dictionary)
		examinee = SRDOConsumer(node)
		
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
		examinee = SRDOConsumer(node)
		network = Network()
		
		node.attach(network)
		
		with self.assertRaises(RuntimeError):
			examinee.detach()
		
		test_data = [-1, 0x100000000]
		for value in test_data:
			with self.subTest(value = value):
				with self.assertRaises(ValueError):
					examinee.attach(value, 0, 0)
				with self.assertRaises(ValueError):
					examinee.attach(0, value, 0)
				with self.assertRaises(ValueError):
					examinee.attach(0, 0, value)
		
		examinee.attach()
		self.assertTrue(examinee.is_attached())
		
		examinee.attach((1 << 29) | 0xFF + 2 * node.id, (1 << 29) | 0x100 + 2 * node.id)
		self.assertTrue(examinee.is_attached())
		
		examinee.detach()
		self.assertFalse(examinee.is_attached())
		
		node.detach()
	
	def test_on_message(self):
		bus1 = can.Bus(interface = "virtual", channel = 0)
		bus2 = can.Bus(interface = "virtual", channel = 0)
		dictionary = ObjectDictionary()
		node = Node("a", 1, dictionary)
		examinee = SRDOConsumer(node)
		network = Network()
		
		network.attach(bus1)
		node.attach(network)
		examinee.attach()
		
		#### Test step: Correct frame pair
		message = can.Message(arbitration_id = 0xFF + 2 * node.id, is_extended_id = False, is_remote_frame = False, data = b"\x00")
		bus2.send(message)
		time.sleep(0.01)
		
		self.assertEqual(examinee.normal_data, b"\x00")
		
		message = can.Message(arbitration_id = 0x100 + 2 * node.id, is_extended_id = False, is_remote_frame = False, data = b"\xFF")
		bus2.send(message)
		time.sleep(0.01)
		
		self.assertEqual(examinee.complement_data, b"\xFF")
		
		#### Test step: Ignore RTR
		message = can.Message(arbitration_id = 0xFF + 2 * node.id, is_extended_id = False, is_remote_frame = True, dlc = 1)
		bus2.send(message)
		time.sleep(0.01)
		
		self.assertEqual(examinee.normal_data, b"\x00")
		
		message = can.Message(arbitration_id = 0x100 + 2 * node.id, is_extended_id = False, is_remote_frame = True, dlc = 1)
		bus2.send(message)
		time.sleep(0.01)
		
		self.assertEqual(examinee.complement_data, b"\xFF")
		
		#### Test step: Ignore wrong frame type
		message = can.Message(arbitration_id = 0xFF + 2 * node.id, is_extended_id = True, is_remote_frame = False, data = b"\x00")
		bus2.send(message)
		time.sleep(0.01)
		
		self.assertEqual(examinee.normal_data, b"\x00")
		
		message = can.Message(arbitration_id = 0x100 + 2 * node.id, is_extended_id = True, is_remote_frame = False, data = b"\xFF")
		bus2.send(message)
		time.sleep(0.01)
		
		self.assertEqual(examinee.complement_data, b"\xFF")
		
		#### Test step: Correct frame pair, service just collects
		message = can.Message(arbitration_id = 0xFF + 2 * node.id, is_extended_id = False, is_remote_frame = False, data = b"\xAA")
		bus2.send(message)
		time.sleep(0.01)
		
		self.assertEqual(examinee.normal_data, b"\xAA")
		
		message = can.Message(arbitration_id = 0x100 + 2 * node.id, is_extended_id = False, is_remote_frame = False, data = b"\xCC")
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
		dictionary = ObjectDictionary()
		node = Node("a", 1, dictionary)
		examinee = SRDOConsumer(node)
		network = Network()
		
		cb1 = Mock()
		examinee.add_callback("sync", cb1)
		
		network.attach(bus1)
		node.attach(network)
		examinee.attach()
		
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


if __name__ == "__main__":
	unittest.main()
