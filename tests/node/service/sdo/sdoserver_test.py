import unittest
import time
import struct
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
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, b"\x80\x00\x00\x00\x01\x00\x04\x05")
		
		# Block download -> Not implemented and thus the response is an abort
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = b"\xC0\x00\x00\x00\x00\x00\x00\x00")
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, b"\x80\x00\x00\x00\x01\x00\x04\x05")
		
		# Network indication -> Not implemented and thus the response is an abort
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = b"\xE0\x00\x00\x00\x00\x00\x00\x00")
		bus2.send(message)
		
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
		dictionary["rec"].append(canopen.objectdictionary.Variable("boolean", 0x1234, 0x01, 0x01, "rw"))
		dictionary["rec"].append(canopen.objectdictionary.Variable("integer8", 0x1234, 0x02, 0x02, "rw"))
		dictionary["rec"].append(canopen.objectdictionary.Variable("integer16", 0x1234, 0x03, 0x03, "rw"))
		dictionary["rec"].append(canopen.objectdictionary.Variable("integer32", 0x1234, 0x04, 0x04, "rw"))
		dictionary["rec"].append(canopen.objectdictionary.Variable("unsigned8", 0x1234, 0x05, 0x05, "ro"))
		dictionary["rec"].append(canopen.objectdictionary.Variable("unsigned16", 0x1234, 0x06, 0x06, "wo"))
		dictionary["rec"].append(canopen.objectdictionary.Variable("domain", 0x1234, 0x0F, 0x0F, "rw"))
		dictionary["rec"].append(canopen.objectdictionary.Variable("integer24", 0x1234, 0x10, 0x10, "rw"))
		dictionary["rec"].append(canopen.objectdictionary.Variable("integer40", 0x1234, 0x11, 0x11, "rw"))
		dictionary["rec"].append(canopen.objectdictionary.Variable("integer48", 0x1234, 0x12, 0x12, "rw"))
		dictionary.append(canopen.objectdictionary.Variable("var", 0x5678, 0x00, 0x07, "rw"))
		node = canopen.Node("a", 1, dictionary)
		sdoserver = canopen.node.service.SDOServer()
		
		network.attach(bus1)
		node.attach(network)
		sdoserver.attach(node)
		
		#### Test step
		# Initiate: index: - -> Abort with index unknown
		d = struct.pack("<BHBL", 0x20, 0x0000, 0x00, 0x00000000)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data,struct.pack("<BHBL", 0x80, 0x0000, 0x00, 0x06020000))
		
		#### Test step
		# Initiate: index: +, subindex: - -> Abort with subindex unknown
		d = struct.pack("<BHBL", 0x20, 0x1234, 0x99, 0x00000000)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, 0x1234, 0x99, 0x06090011))
		
		#### Test step
		# Initiate: index: +, subindex: +, rw: - -> Abort with attempt to write an read only object
		d = struct.pack("<BHBL", 0x20, 0x1234, 0x05, 0x00000000)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, 0x1234, 0x05, 0x06010002))
		
		#### Test step
		# Segment: No active segmented transfer -> Abort
		d = struct.pack("<B7s", 0x00, b"\x00\x00\x00\x00\x00\x00\x00")
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, 0x0000, 0x00, 0x05040001))
		
		#### Test step
		# Initiate: index: +, subindex: +, rw: +, e = 0 & s = 0 & n = 0 -> Abort with command invalid
		d = struct.pack("<BHBL", 0x20, 0x1234, 0x0F, 0x00000000)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, 0x1234, 0x0F, 0x05040001))
		
		#### Test step
		# Initiate: e = 0 & s = 1 & size in data -> Confirm
		d = struct.pack("<BHBL", 0x21, 0x1234, 0x0F, 0x00000004)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x60, 0x1234, 0x0F, 0x00000000))
		
		# Segment: Wrong toggle bit -> Abort
		d = struct.pack("<B7s", 0x10, b"\x00\x00\x00\x00\x00\x00\x00")
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, 0x1234, 0x0F, 0x05030000))
		
		#### Test step
		# Initiate: e = 0 & s = 1 & size in data -> Confirm
		d = struct.pack("<BHBL", 0x21, 0x1234, 0x0F, 0x00000008)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x60, 0x1234, 0x0F, 0x00000000))
		
		# Segment: Correct toggle bit -> Confirm
		d = struct.pack("<B7s", 0x0A, b"\x11\x22\x00\x00\x00\x00\x00")
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<B7s", 0x20, b"\x00\x00\x00\x00\x00\x00\x00"))
		
		# Segment: Correct toggle bit, Close transfer / Last segment, but wrong amount of data (missing segments) -> Abort
		d = struct.pack("<B7s", 0x1B, b"\x33\x44\x00\x00\x00\x00\x00")
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, 0x1234, 0x0F, 0x06070010))
		
		#### Test step
		# Initiate: e = 0 & s = 1 & size in data -> Confirm
		d = struct.pack("<BHBL", 0x21, 0x5678, 0x00, 0x00000004)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x60, 0x5678, 0x00, 0x00000000))
		
		# Segment: Correct toggle bit -> Confirm
		d = struct.pack("<B7s", 0x0A, b"\x11\x22\x00\x00\x00\x00\x00")
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<B7s", 0x20, b"\x00\x00\x00\x00\x00\x00\x00"))
		
		# Delete Variable from dictionary
		del dictionary["var"]
		
		# Segment: Correct toggle bit, Close transfer / Last segment, variable does not exist (dictionary have been altered) -> Abort
		d = struct.pack("<B7s", 0x1B, b"\x33\x44\x00\x00\x00\x00\x00")
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, 0x5678, 0x00, 0x06020000))
		
		# Restore Variable in dictionary
		dictionary.append(canopen.objectdictionary.Variable("var", 0x5678, 0x00, 0x07, "rw"))
		
		#### Test step
		# Initiate: e = 0 & s = 1 & size in data -> Confirm
		d = struct.pack("<BHBL", 0x21, 0x1234, 0x0F, 0x00000004)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x60, 0x1234, 0x0F, 0x00000000))
		
		# Segment: Correct toggle bit -> Confirm
		d = struct.pack("<B7s", 0x0A, b"\x11\x22\x00\x00\x00\x00\x00")
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<B7s", 0x20, b"\x00\x00\x00\x00\x00\x00\x00"))
		
		# Delete Variable from dictionary
		del dictionary["rec"]["domain"]
		
		# Segment: Correct toggle bit, Close transfer / Last segment, variable does not exist (dictionary have been altered) -> Abort
		d = struct.pack("<B7s", 0x1B, b"\x33\x44\x00\x00\x00\x00\x00")
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, 0x1234, 0x0F, 0x06090011))
		
		# Restore Variable in dictionary
		dictionary["rec"].append(canopen.objectdictionary.Variable("domain", 0x1234, 0x0F, 0x0F, "rw"))
		
		#### Test step
		# Initiate: e = 0 & s = 1 & size in data -> Confirm
		d = struct.pack("<BHBL", 0x21, 0x1234, 0x12, 0x00000004)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x60, 0x1234, 0x12, 0x00000000))
		
		# Segment: Correct toggle bit -> Confirm
		d = struct.pack("<B7s", 0x0A, b"\x11\x22\x00\x00\x00\x00\x00")
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<B7s", 0x20, b"\x00\x00\x00\x00\x00\x00\x00"))
		
		# Segment: Correct toggle bit, Close transfer / Last segment, but wrong amount of data (size of variable higher than transfered data) -> Abort
		d = struct.pack("<B7s", 0x1B, b"\x33\x44\x00\x00\x00\x00\x00")
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, 0x1234, 0x12, 0x06070010))
		
		#### Test step
		# Initiate: e = 0 & s = 1 & size in data -> Confirm
		d = struct.pack("<BHBL", 0x21, 0x1234, 0x0F, 0x00000004)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x60, 0x1234, 0x0F, 0x00000000))
		
		# Segment: Correct toggle bit -> Confirm
		d = struct.pack("<B7s", 0x0A, b"\x11\x22\x00\x00\x00\x00\x00")
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<B7s", 0x20, b"\x00\x00\x00\x00\x00\x00\x00"))
		
		# Segment: Correct toggle bit, Close transfer / Last segment -> Confirm
		d = struct.pack("<B7s", 0x1B, b"\x33\x44\x00\x00\x00\x00\x00")
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<B7s", 0x30, b"\x00\x00\x00\x00\x00\x00\x00"))
		
		#### Test step
		# Initiate: e = 0 & s = 1 & size in data -> Confirm
		d = struct.pack("<BHBL", 0x21, 0x5678, 0x00, 0x00000004)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x60, 0x5678, 0x00, 0x00000000))
		
		# Segment: Correct toggle bit -> Confirm
		d = struct.pack("<B7s", 0x0A, b"\x11\x22\x00\x00\x00\x00\x00")
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<B7s", 0x20, b"\x00\x00\x00\x00\x00\x00\x00"))
		
		# Segment: Correct toggle bit, Close transfer / Last segment -> Confirm
		d = struct.pack("<B7s", 0x1B, b"\x33\x44\x00\x00\x00\x00\x00")
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<B7s", 0x30, b"\x00\x00\x00\x00\x00\x00\x00"))
		
		#### Test step
		# Initiate: index: +, subindex: +, rw: +, e = 1 & s = 0 & n = 0 -> Abort on variable with 5 bytes or more
		d = struct.pack("<BHBL", 0x22, 0x1234, 0x11, 0x00000000)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, 0x1234, 0x11, 0x06070010))
		
		#### Test step
		# Initiate: index: +, subindex: +, rw: +, e = 1 & s = 0 & n = 0 -> Confirm on variable with 4 bytes length or less
		d = struct.pack("<BHBL", 0x22, 0x5678, 0x00, 0x00000000)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x60, 0x5678, 0x00, 0x00000000))
		
		#### Test step
		# Initiate: index: +, subindex: +, rw: +, e = 1 & s = 1 & n = 0 -> Abort on variable with 5 bytes or more
		d = struct.pack("<BHBL", 0x23, 0x1234, 0x12, 0x00000000)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, 0x1234, 0x12, 0x06070010))
		
		#### Test step
		# Initiate: index: +, subindex: +, rw: +, e = 1 & s = 1 & n = 0 -> Confirm on variable with 4 bytes length or less
		d = struct.pack("<BHBL", 0x23, 0x1234, 0x04, 0x00000000)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x60, 0x1234, 0x04, 0x00000000))
		
		#### Test step
		# Initiate: index: +, subindex: +, rw: +, e = 1 & s = 1 & n = 1 -> Abort on variable with 4 bytes or more
		d = struct.pack("<BHBL", 0x27, 0x1234, 0x04, 0x00000000)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, 0x1234, 0x04, 0x06070010))
		
		#### Test step
		# Initiate: index: +, subindex: +, rw: +, e = 1 & s = 1 & n = 1 -> Confirm on variable with 3 bytes length or less
		d = struct.pack("<BHBL", 0x27, 0x1234, 0x10, 0x00000000)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x60, 0x1234, 0x10, 0x00000000))
		
		#### Test step
		# Initiate: index: +, subindex: +, rw: +, e = 1 & s = 1 & n = 2 -> Abort on variable with 3 bytes or more
		d = struct.pack("<BHBL", 0x2B, 0x1234, 0x10, 0x00000000)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, 0x1234, 0x10, 0x06070010))
		
		#### Test step
		# Initiate: index: +, subindex: +, rw: +, e = 1 & s = 1 & n = 2 -> Confirm on variable with 2 bytes length or less
		d = struct.pack("<BHBL", 0x2B, 0x1234, 0x03, 0x00000000)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x60, 0x1234, 0x03, 0x00000000))
		
		#### Test step
		# Initiate: index: +, subindex: +, rw: +, e = 1 & s = 1 & n = 3 -> Abort on variable with 2 bytes or more
		d = struct.pack("<BHBL", 0x2F, 0x1234, 0x03, 0x00000000)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, 0x1234, 0x03, 0x06070010))
		
		#### Test step
		# Initiate: index: +, subindex: +, rw: +, e = 1 & s = 1 & n = 3 -> Confirm on variable with 1 bytes length
		d = struct.pack("<BHBL", 0x2F, 0x1234, 0x01, 0x00000000)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x60, 0x1234, 0x01, 0x00000000))
		
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
		dictionary["rec"].append(canopen.objectdictionary.Variable("boolean", 0x1234, 0x01, 0x01, "rw"))
		dictionary["rec"].append(canopen.objectdictionary.Variable("integer8", 0x1234, 0x02, 0x02, "rw"))
		dictionary["rec"].append(canopen.objectdictionary.Variable("integer16", 0x1234, 0x03, 0x03, "rw"))
		dictionary["rec"].append(canopen.objectdictionary.Variable("integer32", 0x1234, 0x04, 0x04, "rw"))
		dictionary["rec"].append(canopen.objectdictionary.Variable("unsigned8", 0x1234, 0x05, 0x05, "ro"))
		dictionary["rec"].append(canopen.objectdictionary.Variable("unsigned16", 0x1234, 0x06, 0x06, "wo"))
		dictionary["rec"].append(canopen.objectdictionary.Variable("domain", 0x1234, 0x0F, 0x0F, "rw"))
		dictionary["rec"].append(canopen.objectdictionary.Variable("integer24", 0x1234, 0x10, 0x10, "rw"))
		dictionary["rec"].append(canopen.objectdictionary.Variable("integer40", 0x1234, 0x11, 0x11, "rw"))
		dictionary.append(canopen.objectdictionary.Variable("var", 0x5678, 0x00, 0x0007, "rw"))
		node = canopen.Node("a", 1, dictionary)
		sdoserver = canopen.node.service.SDOServer()
		
		network.attach(bus1)
		node.attach(network)
		sdoserver.attach(node)
		
		#### Test step
		# Initiate: index: - -> Abort with index unknown
		d = struct.pack("<BHBL", 0x40, 0x0000, 0x00, 0x00000000)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data,struct.pack("<BHBL", 0x80, 0x0000, 0x00, 0x06020000))
		
		#### Test step
		# Initiate: index: +, subindex: - -> Abort with subindex unknown
		d = struct.pack("<BHBL", 0x40, 0x1234, 0x99, 0x00000000)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, 0x1234, 0x99, 0x06090011))
		
		#### Test step
		# Initiate: index: +, subindex: +, rw: - -> Abort with attempt to read an write only object
		d = struct.pack("<BHBL", 0x40, 0x1234, 0x06, 0x00000000)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, 0x1234, 0x06, 0x06010001))
		
		#### Test step
		# Segment: No active segmented transfer -> Abort
		d = struct.pack("<B7s", 0x60, b"\x00\x00\x00\x00\x00\x00\x00")
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, 0x0000, 0x00, 0x05040001))
		
		#### Test step
		# Initiate: index: +, subindex: +, rw: + -> Confirm expedited transfer
		d = struct.pack("<BHBL", 0x40, 0x5678, 0x00, 0x00000000)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x43, 0x5678, 0x00, 0x00000000))
		
		#### Test step
		# Initiate: index: +, subindex: +, rw: + -> Confirm segmented transfer
		d = struct.pack("<BHBL", 0x40, 0x1234, 0x11, 0x00000000)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x41, 0x1234, 0x11, 0x00000008))
		
		# Segment: Wrong toggle bit -> Abort
		d = struct.pack("<B7s", 0x70, b"\x00\x00\x00\x00\x00\x00\x00")
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, 0x1234, 0x11, 0x05030000))

		#### Test step
		# Initiate: index: +, subindex: +, rw: + -> Confirm segmented transfer
		d = struct.pack("<BHBL", 0x40, 0x1234, 0x11, 0x00000000)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x41, 0x1234, 0x11, 0x00000008))
		
		# Segment: Correct toggle bit -> Data segment
		d = struct.pack("<B7s", 0x60, b"\x00\x00\x00\x00\x00\x00\x00")
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<B7s", 0x00, b"\x00\x00\x00\x00\x00\x00\x00"))

		# Segment: Wrong toggle bit -> Abort
		d = struct.pack("<B7s", 0x60, b"\x00\x00\x00\x00\x00\x00\x00")
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, 0x1234, 0x11, 0x05030000))

		#### Test step
		# Initiate: index: +, subindex: +, rw: + -> Confirm segmented transfer
		d = struct.pack("<BHBL", 0x40, 0x1234, 0x11, 0x00000000)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x41, 0x1234, 0x11, 0x00000008))
		
		# Segment: Correct toggle bit -> Data segment
		d = struct.pack("<B7s", 0x60, b"\x00\x00\x00\x00\x00\x00\x00")
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<B7s", 0x00, b"\x00\x00\x00\x00\x00\x00\x00"))

		# Segment: Correct toggle bit -> Last segment
		d = struct.pack("<B7s", 0x70, b"\x00\x00\x00\x00\x00\x00\x00")
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<B7s", 0x1D, b"\x00\x00\x00\x00\x00\x00\x00"))
		
		sdoserver.detach()
		node.detach()
		network.detach()
		bus1.shutdown()
		bus2.shutdown()


if __name__ == "__main__":
	unittest.main()
