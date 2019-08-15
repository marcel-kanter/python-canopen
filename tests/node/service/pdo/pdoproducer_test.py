import unittest
from unittest.mock import Mock
import time
import can
import canopen
from canopen.node.service.pdo import PDOProducer


class PDOProducerTest(unittest.TestCase):
	def test_init(self):
		examinee = PDOProducer()
		
		self.assertEqual(examinee.node, None)
	
	def test_attach_detach(self):
		network = canopen.Network()
		dictionary = canopen.ObjectDictionary()
		node1 = canopen.Node("a", 1, dictionary)
		node2 = canopen.Node("b", 2, dictionary)
		examinee = PDOProducer()
		
		network.append(node1)
		network.append(node2)
				
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
		
		del network[node1.name]
		del network[node2.name]

	def test_pdo(self):
		bus1 = can.Bus(interface = "virtual", channel = 0)
		bus2 = can.Bus(interface = "virtual", channel = 0)
		network = canopen.Network()
		dictionary = canopen.ObjectDictionary()
		node = canopen.Node("a", 1, dictionary)
		examinee = PDOProducer()
		
		m = Mock()
		examinee.add_callback("pdo", m)
		
		network.attach(bus1)
		node.attach(network)
		examinee.attach(node)
		
		#### Test step: standard frame -> ignored
		message = can.Message(arbitration_id = 0x181, is_extended_id = False, data = b"\x00\x00\x00\x00\x00\x00\x00\x00")
		bus2.send(message)
		time.sleep(0.001)
		
		m.assert_not_called()
		
		#### Test step: Remote transmission of PDO
		message = can.Message(arbitration_id = 0x181, is_extended_id = False, is_remote_frame = True, dlc = 8)
		bus2.send(message)
		time.sleep(0.001)
		
		m.assert_called()
		
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
		examinee = PDOProducer()
		
		m = Mock()
		examinee.add_callback("sync", m)
		
		network.attach(bus1)
		node.attach(network)
		examinee.attach(node)
				
		#### Test step: Sync message
		message = can.Message(arbitration_id = 0x80, is_extended_id = False, data = b"\x01")
		bus2.send(message)
		time.sleep(0.001)
		
		m.assert_called()
		
		examinee.detach()
		node.detach()
		network.detach()
		bus1.shutdown()
		bus2.shutdown()


if __name__ == "__main__":
	unittest.main()
