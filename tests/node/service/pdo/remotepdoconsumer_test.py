import unittest
import can
import canopen
from canopen.node.service.pdo import RemotePDOConsumer


class RemotePDOConsumerTest(unittest.TestCase):
	def test_init(self):
		test_data = [-1, 241, 253, 256]
		for value in test_data:
			with self.assertRaises(ValueError):
				RemotePDOConsumer(value)
		
		examinee = RemotePDOConsumer()
		
		self.assertEqual(examinee.node, None)
		
		test_data = [-1, 241, 253, 256]
		for value in test_data:
			with self.assertRaises(ValueError):
				examinee.transmission_type = value
		
		test_data = [0, 1, 2, 3, 4, 8, 240, 254, 255]
		for value in test_data:
			examinee.transmission_type = value
			self.assertEqual(examinee.transmission_type, value)
		
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
		examinee = RemotePDOConsumer()
		
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
					examinee.attach(node1, value)
		
		examinee.attach(node1)
		self.assertEqual(examinee.node, node1)
		
		with self.assertRaises(ValueError):
			examinee.attach(node1)
		
		examinee.attach(node2, (1 << 29) | (0x200 + node2.id))
		self.assertEqual(examinee.node, node2)
		
		examinee.detach()
		self.assertEqual(examinee.node, None)
		
		del network[node1.name]
		del network[node2.name]
	
	def test_send(self):
		bus1 = can.Bus(interface = "virtual", channel = 0)
		bus2 = can.Bus(interface = "virtual", channel = 0)
		network = canopen.Network()
		dictionary = canopen.ObjectDictionary()
		node = canopen.Node("a", 1, dictionary)
		examinee = RemotePDOConsumer()
		
		network.attach(bus1)
		node.attach(network)
		
		examinee.data = None
		with self.assertRaises(RuntimeError):
			examinee.send()
		
		cob_id_txs = [0x201, (1 << 29) | 0x201]
		for cob_id_tx in cob_id_txs:
			examinee.attach(node, cob_id_tx)
			
			with self.subTest("cub_id_tx=" + hex(cob_id_tx)):
				data = b"\x00"
				examinee.data = data
				examinee.send()
				
				message = bus2.recv(0.1)
				self.assertEqual(message.arbitration_id, 0x201)
				self.assertEqual(message.is_extended_id, bool(cob_id_tx & (1 << 29)))
				self.assertEqual(message.data, data)
				
			examinee.detach()
		
		node.detach()
		network.detach()
		bus1.shutdown()
		bus2.shutdown()


if __name__ == "__main__":
	unittest.main()
