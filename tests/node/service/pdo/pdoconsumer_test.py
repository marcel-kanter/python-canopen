import unittest
from unittest.mock import Mock
import time
import can
import canopen
from canopen.node.service.pdo import PDOConsumer


class PDOConsumerTest(unittest.TestCase):
	def test_init(self):
		examinee = PDOConsumer()
		
		self.assertEqual(examinee.node, None)
		
		test_data = [None, b"\x22", b"\x11\x00"]
		for value in test_data:
			with self.subTest(value = value):
				examinee.data = value
				self.assertEqual(examinee.data, value)
	
	def test_attach_detach(self):
		network = canopen.Network()
		dictionary = canopen.ObjectDictionary()
		node1 = canopen.Node("a", 1, dictionary)
		node2 = canopen.Node("b", 2, dictionary)
		examinee = PDOConsumer()
		
		network.add(node1)
		network.add(node2)
		
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
		
		examinee.attach(node2, (1 << 29) | (0x200 + node2.id), (1 << 29) | 0x80)
		self.assertEqual(examinee.node, node2)
		
		examinee.detach()
		self.assertEqual(examinee.node, None)
		
		del network[node1.name]
		del network[node2.name]
	
	def test_pdo(self):
		bus1 = can.Bus(interface = "virtual", channel = 0)
		bus2 = can.Bus(interface = "virtual", channel = 0)
		network = canopen.Network()
		dictionary = canopen.ObjectDictionary()
		node = canopen.Node("a", 1, dictionary)
		examinee = PDOConsumer()
		
		cb1 = Mock()
		examinee.add_callback("pdo", cb1)
		
		network.attach(bus1)
		node.attach(network)
		
		examinee.attach(node)
		
		#### Test step: PDO message
		test_data = [b"\x11\x22\x33\x44\x55\x66\x77\x88", b"\x00", b""]
		for data in test_data:
			with self.subTest("PDO message", data = data):
				cb1.reset_mock()
				message = can.Message(arbitration_id = 0x201, is_extended_id = False, data = data)
				bus2.send(message)
				time.sleep(0.001)
				cb1.assert_called()
				self.assertEqual(examinee.data, data)
		
		#### Test step: PDO message, ignore differend extended frame type
		cb1.reset_mock()
		message = can.Message(arbitration_id = 0x201, is_extended_id = True, data = b"\x11\x22\x33\x44\x55\x66\x77\x88")
		bus2.send(message)
		time.sleep(0.01)
		cb1.assert_not_called()
		
		#### Test step: PDO message, ignore remote frame
		cb1.reset_mock()
		message = can.Message(arbitration_id = 0x201, is_extended_id = False, is_remote_frame = True, dlc = 1)
		bus2.send(message)
		time.sleep(0.01)
		cb1.assert_not_called()
		
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
		examinee = PDOConsumer()
		
		cb1 = Mock()
		examinee.add_callback("sync", cb1)
		
		network.attach(bus1)
		node.attach(network)
		examinee.attach(node)
		
		#### Test step: Sync message
		test_data = [None, b"", b"\x01"]
		for data in test_data:
			with self.subTest("sync message", data = data):
				cb1.reset_mock()
				message = can.Message(arbitration_id = 0x80, is_extended_id = False, data = data)
				bus2.send(message)
				time.sleep(0.001)
				cb1.assert_called()
		
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
