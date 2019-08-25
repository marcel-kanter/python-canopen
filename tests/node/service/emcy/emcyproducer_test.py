import unittest
import struct
import can
import canopen.node.service
from canopen.emcy.errorcodes import *


class EMCYProducerTestCase(unittest.TestCase):
	def test_init(self):
		canopen.node.service.EMCYProducer()
	
	def test_attach_detach(self):
		dictionary = canopen.ObjectDictionary()
		network = canopen.Network()
		node1 = canopen.Node("a", 1, dictionary)
		node2 = canopen.Node("b", 2, dictionary)
		examinee = canopen.node.service.EMCYProducer()
		
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
					examinee.attach(node1, value)
		
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
		examinee = canopen.node.service.EMCYProducer()
		
		network.attach(bus1)
		node.attach(network)
		examinee.attach(node)
		
		#### Test step: Invalid value ranges
		error_register = 0
		data = None
		for error_code in [-1, -100, 0x10000]:
			with self.assertRaises(ValueError):
				examinee.send(error_code, error_register, data)
		
		error_code = 0
		data = None
		for error_register in [-1, -100, 0x100]:
			with self.assertRaises(ValueError):
				examinee.send(error_code, error_register, data)
		
		error_code = 0
		error_register = 0
		data = b"\x01\x02\x03\x04\x05\x06"
		with self.assertRaises(ValueError):
			examinee.send(error_code, error_register, data)
		
		#### Test step: Send error without data
		error_code = 0
		error_register = 0
		data = None
		examinee.send(error_code, error_register, data)
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x80 + node.id)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<HB5s", error_code, error_register, b"\x00\x00\x00\x00\x00"))
		
		#### Test step: Send error with some data
		error_code = 0
		error_register = 0
		data = b"\x01\x02"
		examinee.send(error_code, error_register, data)
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x80 + node.id)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<HB5s", error_code, error_register, b"\x01\x02\x00\x00\x00"))
		
		#### Test step: Send some error_codes
		test_data = [(NO_ERROR, 0x00), (GENERIC_ERROR, 0x10), (SOFTWARE_ERROR, 0x14)]
		for value in test_data:
			with self.subTest(value = value):
				error_code = value[0]
				error_register = value[1]
				data = b"\x01\x02"
				examinee.send(error_code, error_register, data)
				message_recv = bus2.recv(1)
				self.assertEqual(message_recv.arbitration_id, 0x80 + node.id)
				self.assertEqual(message_recv.is_extended_id, False)
				self.assertEqual(message_recv.data, struct.pack("<HB5s", error_code, error_register, b"\x01\x02\x00\x00\x00"))
		
		examinee.detach()
		
		examinee.attach(node, (1 << 29) | (0x80 + node.id))
		
		#### Test step: Send some error_codes
		test_data = [(NO_ERROR, 0x00), (GENERIC_ERROR, 0x10), (SOFTWARE_ERROR, 0x14)]
		for value in test_data:
			with self.subTest(value = value):
				error_code = value[0]
				error_register = value[1]
				data = b"\x01\x02"
				examinee.send(error_code, error_register, data)
				message_recv = bus2.recv(1)
				self.assertEqual(message_recv.arbitration_id, 0x80 + node.id)
				self.assertEqual(message_recv.is_extended_id, True)
				self.assertEqual(message_recv.data, struct.pack("<HB5s", error_code, error_register, b"\x01\x02\x00\x00\x00"))
		
		examinee.detach()
		
		node.detach()
		network.detach()
		bus1.shutdown()
		bus2.shutdown()


if __name__ == "__main__":
	unittest.main()
