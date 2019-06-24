import unittest
import time
import struct
import can
import canopen.node.service


class SDOClientTestCase(unittest.TestCase):
	def test_init(self):
		canopen.node.service.SDOClient()
	
	def test_attach_detach(self):
		network = canopen.Network()
		dictionary = canopen.ObjectDictionary()
		node1 = canopen.Node("a", 1, dictionary)
		node2 = canopen.Node("b", 2, dictionary)
		examinee = canopen.node.service.SDOClient()
		
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

	def test_on_response(self):
		bus1 = can.Bus(interface = "virtual", channel = 0)
		bus2 = can.Bus(interface = "virtual", channel = 0)
		network = canopen.Network()
		dictionary = canopen.ObjectDictionary()
		node = canopen.Node("a", 1, dictionary)
		sdoclient = canopen.node.service.SDOClient()
		
		network.attach(bus1)
		node.attach(network)
		sdoclient.attach(node)
		
		# Wrong data length -> Ignored by SDOClient
		message_send = can.Message(arbitration_id = 0x581, is_extended_id = False, data = b"\x00")
		bus2.send(message_send)
		time.sleep(0.001)
		
		# Segment upload -> Currently abort
		d = struct.pack("<BHB4s", 0x00, 0x0000, 0x00, b"\x00\x00\x00\x00")
		message = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, 0x0000, 0x00, 0x05040001))
		
		# Segment download -> Currently abort
		d = struct.pack("<BHB4s", 0x20, 0x0000, 0x00, b"\x00\x00\x00\x00")
		message = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, 0x0000, 0x00, 0x05040001))
		
		# Initiate upload -> Currently abort
		d = struct.pack("<BHB4s", 0x40, 0x0000, 0x00, b"\x00\x00\x00\x00")
		message = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, 0x0000, 0x00, 0x05040001))
		
		# Initiate download -> Currently abort
		d = struct.pack("<BHB4s", 0x60, 0x0000, 0x00, b"\x00\x00\x00\x00")
		message = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, 0x0000, 0x00, 0x05040001))
		
		# Abort transfer -> No response
		d = struct.pack("<BHB4s", 0x80, 0x0000, 0x00, b"\x00\x00\x00\x00")
		message = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message)
		time.sleep(0.001)
		
		# Block download -> Not implemented and thus the response is an abort
		d = struct.pack("<BHB4s", 0xA0, 0x0000, 0x00, b"\x00\x00\x00\x00")
		message = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, 0x0000, 0x00, 0x05040001))
		
		# Block upload -> Not implemented and thus the response is an abort
		d = struct.pack("<BHB4s", 0xC0, 0x0000, 0x00, b"\x00\x00\x00\x00")
		message = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, 0x0000, 0x00, 0x05040001))
		
		# Network indication -> Not implemented and thus the response is an abort
		message = can.Message(arbitration_id = 0x581, is_extended_id = False, data = b"\xE0\x00\x00\x00\x00\x00\x00\x00")
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, 0x0000, 0x00, 0x05040001))
		
		sdoclient.detach()
		node.detach()
		network.detach()
		bus1.shutdown()
		bus2.shutdown()
		

if __name__ == "__main__":
	unittest.main()
