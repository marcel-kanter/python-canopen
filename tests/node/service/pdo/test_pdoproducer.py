import unittest
from unittest.mock import Mock
import time
import can

from canopen import Node, Network
from canopen.objectdictionary import ObjectDictionary
from canopen.node.service.pdo import PDOProducer


class PDOProducerTest(unittest.TestCase):
	def test_init(self):
		dictionary = ObjectDictionary()
		node = Node("n", 1, dictionary)
		
		test_data = [-1, 241, 251, 256]
		for value in test_data:
			with self.assertRaises(ValueError):
				PDOProducer(node, value)
		
		examinee = PDOProducer(node)
		
		self.assertEqual(examinee.node, node)
		
		test_data = [-1, 241, 251, 256]
		for value in test_data:
			with self.assertRaises(ValueError):
				examinee.transmission_type = value
		
		test_data = [0, 1, 2, 3, 4, 8, 240, 252, 253, 254, 255]
		for value in test_data:
			examinee.transmission_type = value
			self.assertEqual(examinee.transmission_type, value)
		
		test_data = [None, b"\x22", b"\x11\x00"]
		for value in test_data:
			with self.subTest(value = value):
				examinee.data = value
				self.assertEqual(examinee.data, value)
	
	def test_attach_detach(self):
		dictionary = ObjectDictionary()
		node = Node("n", 1, dictionary)
		examinee = PDOProducer(node)
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
		
		examinee.attach((1 << 29) | (0x180 + node.id), (1 << 29) | 0x80)
		self.assertTrue(examinee.is_attached())
		
		examinee.detach()
		self.assertFalse(examinee.is_attached())
		
		node.detach()
	
	def test_pdo(self):
		bus1 = can.Bus(interface = "virtual", channel = 0)
		bus2 = can.Bus(interface = "virtual", channel = 0)
		dictionary = ObjectDictionary()
		node = Node("a", 1, dictionary)
		examinee = PDOProducer(node)
		network = Network()
		
		m = Mock()
		examinee.add_callback("rtr", m)
		
		network.attach(bus1)
		node.attach(network)
		examinee.attach()
		
		#### Test step: standard frame -> ignored
		m.reset_mock()
		message = can.Message(arbitration_id = 0x181, is_extended_id = False, data = b"\x00\x00\x00\x00\x00\x00\x00\x00")
		bus2.send(message)
		time.sleep(0.001)
		m.assert_not_called()
		
		#### Test step: Remote transmission of PDO
		m.reset_mock()
		message = can.Message(arbitration_id = 0x181, is_extended_id = False, is_remote_frame = True, dlc = 8)
		bus2.send(message)
		time.sleep(0.001)
		m.assert_called_with("rtr", examinee)
		
		#### Test step: Remote transmission of PDO, but extended frame type differs -> ignored
		m.reset_mock()
		message = can.Message(arbitration_id = 0x181, is_extended_id = True, is_remote_frame = True, dlc = 8)
		bus2.send(message)
		time.sleep(0.001)
		m.assert_not_called()
		
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
		examinee = PDOProducer(node)
		network = Network()
		
		cb1 = Mock()
		examinee.add_callback("sync", cb1)
		
		network.attach(bus1)
		node.attach(network)
		examinee.attach()
		
		#### Test step: Sync message
		cb1.reset_mock()
		message = can.Message(arbitration_id = 0x80, is_extended_id = False, data = b"\x01")
		bus2.send(message)
		time.sleep(0.001)
		cb1.assert_called_with("sync", examinee, 1)
		
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
	
	def test_send(self):
		bus1 = can.Bus(interface = "virtual", channel = 0)
		bus2 = can.Bus(interface = "virtual", channel = 0)
		dictionary = ObjectDictionary()
		node = Node("a", 1, dictionary)
		examinee = PDOProducer(node)
		network = Network()
		
		network.attach(bus1)
		node.attach(network)
		
		examinee.data = None
		with self.assertRaises(RuntimeError):
			examinee.send()
		
		cob_id_txs = [0x181, (1 << 29) | 0x181]
		for cob_id_tx in cob_id_txs:
			examinee.attach(cob_id_tx)
			
			with self.subTest("cub_id_tx=" + hex(cob_id_tx)):
				data = b"\x00"
				examinee.data = data
				examinee.send()
				
				message = bus2.recv(0.1)
				self.assertEqual(message.arbitration_id, 0x181)
				self.assertEqual(message.is_extended_id, bool(cob_id_tx & (1 << 29)))
				self.assertEqual(message.data, data)
				
			examinee.detach()
		
		node.detach()
		network.detach()
		bus1.shutdown()
		bus2.shutdown()


if __name__ == "__main__":
	unittest.main()
