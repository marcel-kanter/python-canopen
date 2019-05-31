import unittest
import time
import can
import canopen.node.service
import canopen.objectdictionary


class SDOServerTestCase(unittest.TestCase):
	def test_init(self):
		canopen.node.service.SDOServer()
	
	def test_attach_detach(self):
		network = canopen.Network()
		dictionary = canopen.ObjectDictionary()
		node1 = canopen.Node("a", 1, dictionary)
		node2 = canopen.Node("b", 2, dictionary)
		sdoserver = canopen.node.service.SDOServer()
		
		node1.attach(network)
		node2.attach(network)
		
		with self.assertRaises(RuntimeError):
			sdoserver.detach()
		
		with self.assertRaises(TypeError):
			sdoserver.attach(None)
		
		sdoserver.attach(node1)
		
		with self.assertRaises(ValueError):
			sdoserver.attach(node1)
		
		sdoserver.attach(node2)
		
		sdoserver.detach()
		
		node1.detach()
		node2.detach()
	
	def test_request(self):
		bus1 = can.Bus(interface = "virtual", channel = 0)
		bus2 = can.Bus(interface = "virtual", channel = 0)
		network = canopen.Network()
		dictionary = canopen.ObjectDictionary()
		node = canopen.Node("a", 1, dictionary)
		sdoserver = canopen.node.service.SDOServer()
		
		network.attach(bus1)
		node.attach(network)
		sdoserver.attach(node)
		
		# Wrong data length -> Ignored by SDOServer
		message_send = can.Message(arbitration_id = 0x601, is_extended_id = False, data = b"\x00")
		bus2.send(message_send)
		time.sleep(0.001)
		
		# Abort transfer -> No response
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = b"\x80\x00\x00\x00\x00\x00\x00\x00")
		bus2.send(message)
		time.sleep(0.001)
		
		# Block upload -> Not implemented and thus the response is an abort
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = b"\xA0\x00\x00\x00\x00\x00\x00\x00")
		bus2.send(message)
		time.sleep(0.010)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, b"\x80\x00\x00\x00\x01\x00\x04\x05")
		
		# Block download -> Not implemented and thus the response is an abort
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = b"\xC0\x00\x00\x00\x00\x00\x00\x00")
		bus2.send(message)
		time.sleep(0.001)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, b"\x80\x00\x00\x00\x01\x00\x04\x05")
		
		# Network indication -> Not implemented and thus the response is an abort
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = b"\xE0\x00\x00\x00\x00\x00\x00\x00")
		bus2.send(message)
		time.sleep(0.001)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, b"\x80\x00\x00\x00\x01\x00\x04\x05")
		
		sdoserver.detach()
		node.detach()
		network.detach()
		bus1.shutdown()
		bus2.shutdown()
	
	def test_download(self):
		bus1 = can.Bus(interface = "virtual", channel = 0)
		bus2 = can.Bus(interface = "virtual", channel = 0)
		network = canopen.Network()
		dictionary = canopen.ObjectDictionary()
		dictionary.append(canopen.objectdictionary.Record("rec", 0x1234))
		dictionary["rec"].append(canopen.objectdictionary.Variable("var1", 0x1234, 0x56, 0x0007, "r"))
		dictionary["rec"].append(canopen.objectdictionary.Variable("var2", 0x1234, 0x78, 0x0007, "w"))
		dictionary["rec"].append(canopen.objectdictionary.Variable("var3", 0x1234, 0x9A, 0x0007, "rw"))
		dictionary.append(canopen.objectdictionary.Variable("var", 0x5678, 0x00, 0x0007, "rw"))
		node = canopen.Node("a", 1, dictionary)
		sdoserver = canopen.node.service.SDOServer()
		
		network.attach(bus1)
		node.attach(network)
		sdoserver.attach(node)
		
		# Download initiate with unknwon index -> Abort with index unknown
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = b"\x20\x00\x00\x00\x00\x00\x00\x00")
		bus2.send(message)
		time.sleep(0.001)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, b"\x80\x00\x00\x00\x00\x00\x02\x06")
		
		# Download initiate with knwon index, but unknown subindex -> Abort with subindex unknown
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = b"\x20\x34\x12\x99\x00\x00\x00\x00")
		bus2.send(message)
		time.sleep(0.001)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, b"\x80\x34\x12\x99\x11\x00\x09\x06")
		
		# Download initiate with knwon index and known subindex, but download is not allowed -> Abort
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = b"\x20\x34\x12\x56\x00\x00\x00\x00")
		bus2.send(message)
		time.sleep(0.001)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, b"\x80\x34\x12\x56\x02\x00\x01\x06")
		
		# Download initiate with knwon index, known subindex and download is allowed
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = b"\x20\x34\x12\x78\x00\x00\x00\x00")
		bus2.send(message)
		time.sleep(0.001)
		
		# Download initiate with knwon index, known subindex and download is allowed
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = b"\x20\x78\x56\x00\x00\x00\x00\x00")
		bus2.send(message)
		time.sleep(0.001)
		
		# Download segment
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = b"\x00\x00\x00\x00\x00\x00\x00\x00")
		bus2.send(message)
		time.sleep(0.001)
		
		sdoserver.detach()
		node.detach()
		network.detach()
		bus1.shutdown()
		bus2.shutdown()
	
	def test_upload(self):
		bus1 = can.Bus(interface = "virtual", channel = 0)
		bus2 = can.Bus(interface = "virtual", channel = 0)
		network = canopen.Network()
		dictionary = canopen.ObjectDictionary()
		dictionary.append(canopen.objectdictionary.Record("rec", 0x1234))
		dictionary["rec"].append(canopen.objectdictionary.Variable("var1", 0x1234, 0x56, 0x0007, "r"))
		dictionary["rec"].append(canopen.objectdictionary.Variable("var2", 0x1234, 0x78, 0x0007, "w"))
		dictionary["rec"].append(canopen.objectdictionary.Variable("var3", 0x1234, 0x9A, 0x0007, "rw"))
		dictionary.append(canopen.objectdictionary.Variable("var", 0x5678, 0x00, 0x0007, "rw"))
		node = canopen.Node("a", 1, dictionary)
		sdoserver = canopen.node.service.SDOServer()
		
		network.attach(bus1)
		node.attach(network)
		sdoserver.attach(node)
		
		# Upload initiate with unknwon index -> Abort with index unknown
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = b"\x40\x00\x00\x00\x00\x00\x00\x00")
		bus2.send(message)
		time.sleep(0.001)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, b"\x80\x00\x00\x00\x00\x00\x02\x06")
		
		# Upload initiate with knwon index, but unknown subindex -> Abort with subindex unknown
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = b"\x40\x34\x12\x99\x00\x00\x00\x00")
		bus2.send(message)
		time.sleep(0.001)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, b"\x80\x34\x12\x99\x11\x00\x09\x06")
		
		# Upload initiate with knwon index and known subindex, but upload is not allowed -> Abort
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = b"\x40\x34\x12\x78\x00\x00\x00\x00")
		bus2.send(message)
		time.sleep(0.001)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, b"\x80\x34\x12\x78\x01\x00\x01\x06")
		
		# Upload initiate with knwon index and known subindex
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = b"\x40\x34\x12\x56\x00\x00\x00\x00")
		bus2.send(message)
		time.sleep(0.001)
		
		# Upload initiate with knwon index and known subindex
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = b"\x40\x78\x56\x00\x00\x00\x00\x00")
		bus2.send(message)
		time.sleep(0.001)
		
		# Upload segment
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = b"\x60\x00\x00\x00\x00\x00\x00\x00")
		bus2.send(message)
		time.sleep(0.001)
		
		sdoserver.detach()
		node.detach()
		network.detach()
		bus1.shutdown()
		bus2.shutdown()


if __name__ == "__main__":
	unittest.main()
