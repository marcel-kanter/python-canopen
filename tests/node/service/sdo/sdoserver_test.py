import unittest
import time
import struct
import can
import canopen.node.service
import canopen.objectdictionary


from tests.node.inspectionnode import InspectionNode


class SDOServerTestCase(unittest.TestCase):
	def test_init(self):
		examinee = canopen.node.service.SDOServer()
		
		examinee.timeout = None
		self.assertEqual(examinee.timeout, None)
		
		examinee.timeout = 1.0
		self.assertEqual(examinee.timeout, 1.0)
		
		with self.assertRaises(ValueError):
			examinee.timeout = 0
		
		with self.assertRaises(ValueError):
			examinee.timeout = -1 
	
	def test_attach_detach(self):
		network = canopen.Network()
		dictionary = canopen.ObjectDictionary()
		node1 = canopen.Node("a", 1, dictionary)
		node2 = canopen.Node("b", 2, dictionary)
		examinee = canopen.node.service.SDOServer()
		
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
		dictionary.add(canopen.objectdictionary.Record("rec", 0x1234))
		dictionary["rec"].add(canopen.objectdictionary.Variable("boolean", 0x1234, 0x01, canopen.objectdictionary.BOOLEAN, "rw"))
		dictionary["rec"].add(canopen.objectdictionary.Variable("integer8", 0x1234, 0x02, canopen.objectdictionary.INTEGER8, "rw"))
		dictionary["rec"].add(canopen.objectdictionary.Variable("integer16", 0x1234, 0x03, canopen.objectdictionary.INTEGER16, "rw"))
		dictionary["rec"].add(canopen.objectdictionary.Variable("integer32", 0x1234, 0x04, canopen.objectdictionary.INTEGER32, "rw"))
		dictionary["rec"].add(canopen.objectdictionary.Variable("unsigned8", 0x1234, 0x05, canopen.objectdictionary.UNSIGNED8, "ro"))
		dictionary["rec"].add(canopen.objectdictionary.Variable("unsigned16", 0x1234, 0x06, canopen.objectdictionary.UNSIGNED16, "wo"))
		dictionary["rec"].add(canopen.objectdictionary.Variable("domain", 0x1234, 0x0F, canopen.objectdictionary.DOMAIN, "rw"))
		dictionary["rec"].add(canopen.objectdictionary.Variable("integer24", 0x1234, 0x10, canopen.objectdictionary.INTEGER24, "rw"))
		dictionary["rec"].add(canopen.objectdictionary.Variable("real64", 0x1234, 0x11, canopen.objectdictionary.REAL64, "rw"))
		dictionary["rec"].add(canopen.objectdictionary.Variable("integer40", 0x1234, 0x12, canopen.objectdictionary.INTEGER40, "rw"))
		dictionary.add(canopen.objectdictionary.Variable("var", 0x5678, 0x00, canopen.objectdictionary.UNSIGNED32, "rw"))
		node = InspectionNode("a", 1, dictionary)
		sdoserver = canopen.node.service.SDOServer()
		
		network.attach(bus1)
		node.attach(network)
		sdoserver.attach(node)
		
		#### Test step
		# Initiate: index: - -> Abort with index unknown
		index = 0x0000
		subindex = 0x00
		d = struct.pack("<BHBL", 0x20, index, subindex, 0x00000000)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data,struct.pack("<BHBL", 0x80, index, subindex, 0x06020000))
		
		#### Test step
		# Initiate: index: +, subindex: - -> Abort with subindex unknown
		index = 0x1234
		subindex = 0x99
		d = struct.pack("<BHBL", 0x20, index, subindex, 0x00000000)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, index, subindex, 0x06090011))
		
		#### Test step
		# Initiate: index: +, subindex: +, rw: - -> Abort with attempt to write an read only object
		index = 0x1234
		subindex = 0x05
		d = struct.pack("<BHBL", 0x20, index, subindex, 0x00000000)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, index, subindex, 0x06010002))
		
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
		index = 0x1234
		subindex = 0x0F
		d = struct.pack("<BHBL", 0x20, index, subindex, 0x00000000)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, index, subindex, 0x05040001))
		
		#### Test step
		# Initiate: e = 0 & s = 1 & size in data -> Confirm
		index = 0x1234
		subindex = 0x0F
		d = struct.pack("<BHBL", 0x21, index, subindex, 0x00000004)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x60, index, subindex, 0x00000000))
		
		# Segment: Wrong toggle bit -> Abort
		d = struct.pack("<B7s", 0x10, b"\x00\x00\x00\x00\x00\x00\x00")
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, index, subindex, 0x05030000))
		
		#### Test step
		# Initiate: e = 0 & s = 1 & size in data -> Confirm
		index = 0x1234
		subindex = 0x0F
		d = struct.pack("<BHBL", 0x21, index, subindex, 0x00000008)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x60, index, subindex, 0x00000000))
		
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
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, index, subindex, 0x06070010))
		
		#### Test step
		# Initiate: e = 0 & s = 1 & size in data -> Confirm
		index = 0x5678
		subindex = 0x00
		d = struct.pack("<BHBL", 0x21, index, subindex, 0x00000004)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x60, index, subindex, 0x00000000))
		
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
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, index, subindex, 0x06020000))
		
		# Restore Variable in dictionary
		dictionary.add(canopen.objectdictionary.Variable("var", 0x5678, 0x00, 0x07, "rw"))
		
		#### Test step
		# Initiate: e = 0 & s = 1 & size in data -> Confirm
		index = 0x1234
		subindex = 0x0F
		d = struct.pack("<BHBL", 0x21, index, subindex, 0x00000004)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x60, index, subindex, 0x00000000))
		
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
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, index, subindex, 0x06090011))
		
		# Restore Variable in dictionary
		dictionary["rec"].add(canopen.objectdictionary.Variable("domain", 0x1234, 0x0F, canopen.objectdictionary.DOMAIN, "rw"))
		
		#### Test step
		# Initiate: e = 0 & s = 1 & size in data -> Confirm
		index = 0x1234
		subindex = 0x12
		d = struct.pack("<BHBL", 0x21, index, subindex, 0x00000004)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x60, index, subindex, 0x00000000))
		
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
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, index, subindex, 0x06070010))
		
		#### Test step
		# Initiate: e = 0 & s = 1 & size in data -> Confirm
		index = 0x1234
		subindex = 0x0F
		d = struct.pack("<BHBL", 0x21, index, subindex, 0x00000004)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x60, index, subindex, 0x00000000))
		
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
		
		#### Test step: Segmented upload with write error in node -> Abort Data cannot be stored in application
		# Initiate: e = 0 & s = 1 & size in data -> Confirm
		index = 0x5678
		subindex = 0x00
		d = struct.pack("<BHBL", 0x21, index, subindex, 0x00000004)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x60, index, subindex, 0x00000000))
		
		# Segment: Correct toggle bit -> Confirm
		d = struct.pack("<B7s", 0x0A, b"\x11\x22\x00\x00\x00\x00\x00")
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<B7s", 0x20, b"\x00\x00\x00\x00\x00\x00\x00"))
		
		# Segment: Correct toggle bit, Close transfer / Last segment -> Abort
		node.raise_exception = True
		d = struct.pack("<B7s", 0x1B, b"\x33\x44\x00\x00\x00\x00\x00")
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, index, subindex, 0x08000020))
		node.raise_exception = False
		
		#### Test step: Segmented upload
		# Initiate: e = 0 & s = 1 & size in data -> Confirm
		index = 0x5678
		subindex = 0x00
		d = struct.pack("<BHBL", 0x21, index, subindex, 0x00000004)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x60, index, subindex, 0x00000000))
		
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
		index = 0x1234
		subindex = 0x11
		d = struct.pack("<BHBL", 0x22, index, subindex, 0x00000000)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, index, subindex, 0x06070010))
		
		#### Test step: Expedited download with write error in node
		# Initiate: index: +, subindex: +, rw: +, e = 1 & s = 0 & n = 0 + Write error in node -> Abort Data cannot be stored in application
		node.raise_exception = True
		index = 0x5678
		subindex = 0x00
		d = struct.pack("<BHBL", 0x22, index, subindex, 0x00000000)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, index, subindex, 0x08000020))
		node.raise_exception = False
		
		#### Test step: Expedited download
		# Initiate: index: +, subindex: +, rw: +, e = 1 & s = 0 & n = 0 -> Confirm on variable with 4 bytes length or less
		index = 0x5678
		subindex = 0x00
		d = struct.pack("<BHBL", 0x22, index, subindex, 0x12345678)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x60, index, subindex, 0x00000000))
		
		self.assertEqual(node[0x5678].value, 0x12345678)
		
		#### Test step
		# Initiate: index: +, subindex: +, rw: +, e = 1 & s = 1 & n = 0 -> Abort on variable with 5 bytes or more
		index = 0x1234
		subindex = 0x12
		d = struct.pack("<BHBL", 0x23, index, subindex, 0x00000000)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, index, subindex, 0x06070010))
		
		#### Test step
		# Initiate: index: +, subindex: +, rw: +, e = 1 & s = 1 & n = 0 -> Confirm on variable with 4 bytes length or less
		index = 0x1234
		subindex = 0x04
		d = struct.pack("<BHBL", 0x23, index, subindex, 0x12345678)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x60, index, subindex, 0x00000000))
		
		self.assertEqual(node[0x1234][0x04].value, 0x12345678)
		
		#### Test step
		# Initiate: index: +, subindex: +, rw: +, e = 1 & s = 1 & n = 1 -> Abort on variable with 4 bytes or more
		index = 0x1234
		subindex = 0x04
		d = struct.pack("<BHBL", 0x27, index, subindex, 0x00000000)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, index, subindex, 0x06070010))
		
		#### Test step
		# Initiate: index: +, subindex: +, rw: +, e = 1 & s = 1 & n = 1 -> Confirm on variable with 3 bytes length or less
		index = 0x1234
		subindex = 0x10
		d = struct.pack("<BHBL", 0x27, index, subindex, 0x87654321)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x60, index, subindex, 0x00000000))
		
		self.assertEqual(node[0x1234][0x10].value, 0x654321)
		
		#### Test step
		# Initiate: index: +, subindex: +, rw: +, e = 1 & s = 1 & n = 2 -> Abort on variable with 3 bytes or more
		index = 0x1234
		subindex = 0x10
		d = struct.pack("<BHBL", 0x2B, index, subindex, 0x00000000)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, index, subindex, 0x06070010))
		
		#### Test step
		# Initiate: index: +, subindex: +, rw: +, e = 1 & s = 1 & n = 2 -> Confirm on variable with 2 bytes length or less
		index = 0x1234
		subindex = 0x03
		d = struct.pack("<BHBL", 0x2B, index, subindex,  0x12345678)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x60, index, subindex, 0x00000000))
		
		self.assertEqual(node[0x1234][0x03].value, 0x5678)
		
		#### Test step
		# Initiate: index: +, subindex: +, rw: +, e = 1 & s = 1 & n = 3 -> Abort on variable with 2 bytes or more
		index = 0x1234
		subindex = 0x03
		d = struct.pack("<BHBL", 0x2F, index, subindex, 0x00000000)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, index, subindex, 0x06070010))
		
		#### Test step
		# Initiate: index: +, subindex: +, rw: +, e = 1 & s = 1 & n = 3 -> Confirm on variable with 1 bytes length
		index = 0x1234
		subindex = 0x02
		d = struct.pack("<BHBL", 0x2F, index, subindex, 0x87654321)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x60, index, subindex, 0x00000000))
		
		self.assertEqual(node[0x1234][0x02].value, 0x21)
		
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
		dictionary.add(canopen.objectdictionary.Record("rec", 0x1234))
		dictionary["rec"].add(canopen.objectdictionary.Variable("boolean", 0x1234, 0x01, canopen.objectdictionary.BOOLEAN, "rw"))
		dictionary["rec"].add(canopen.objectdictionary.Variable("integer8", 0x1234, 0x02, canopen.objectdictionary.INTEGER8, "rw"))
		dictionary["rec"].add(canopen.objectdictionary.Variable("integer16", 0x1234, 0x03, canopen.objectdictionary.INTEGER16, "rw"))
		dictionary["rec"].add(canopen.objectdictionary.Variable("integer32", 0x1234, 0x04, canopen.objectdictionary.INTEGER32, "rw"))
		dictionary["rec"].add(canopen.objectdictionary.Variable("unsigned8", 0x1234, 0x05, canopen.objectdictionary.UNSIGNED8, "ro"))
		dictionary["rec"].add(canopen.objectdictionary.Variable("unsigned16", 0x1234, 0x06, canopen.objectdictionary.UNSIGNED16, "wo"))
		dictionary["rec"].add(canopen.objectdictionary.Variable("domain", 0x1234, 0x0F, canopen.objectdictionary.DOMAIN, "rw"))
		dictionary["rec"].add(canopen.objectdictionary.Variable("integer24", 0x1234, 0x10, canopen.objectdictionary.INTEGER24, "rw"))
		dictionary["rec"].add(canopen.objectdictionary.Variable("real64", 0x1234, 0x11, canopen.objectdictionary.REAL64, "rw"))
		dictionary["rec"].add(canopen.objectdictionary.Variable("integer40", 0x1234, 0x12, canopen.objectdictionary.INTEGER40, "rw"))
		dictionary.add(canopen.objectdictionary.Variable("var", 0x5678, 0x00, canopen.objectdictionary.UNSIGNED32, "rw"))
		node = InspectionNode("a", 1, dictionary)
		sdoserver = canopen.node.service.SDOServer()
		
		network.attach(bus1)
		node.attach(network)
		sdoserver.attach(node)
		
		# Fill in some data
		node[0x5678].value = 12345
		node[0x1234][0x11].value = 0
		
		#### Test step
		# Initiate: index: - -> Abort with index unknown
		index = 0x0000
		subindex = 0x00
		d = struct.pack("<BHBL", 0x40, index, subindex, 0x00000000)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data,struct.pack("<BHBL", 0x80, index, subindex, 0x06020000))
		
		#### Test step
		# Initiate: index: +, subindex: - -> Abort with subindex unknown
		index = 0x1234
		subindex = 0x99
		d = struct.pack("<BHBL", 0x40, index, subindex, 0x00000000)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, index, subindex, 0x06090011))
		
		#### Test step
		# Initiate: index: +, subindex: +, rw: - -> Abort with attempt to read an write only object
		index = 0x1234
		subindex = 0x06
		d = struct.pack("<BHBL", 0x40, index, subindex, 0x00000000)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, index, subindex, 0x06010001))
		
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
		# Initiate: index: +, subindex: +, rw: + with read error in node -> Abort no data available
		node.raise_exception = True
		index = 0x5678
		subindex = 0x00
		d = struct.pack("<BHBL", 0x40, index, subindex, 0x00000000)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, index, subindex, 0x08000024))
		node.raise_exception = False
		
		#### Test step
		# Initiate: index: +, subindex: +, rw: + -> Confirm expedited transfer
		index = 0x5678
		subindex = 0x00
		d = struct.pack("<BHBL", 0x40, index, subindex, 0x00000000)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x43, index, subindex, 12345))
		
		#### Test step
		# Initiate: index: +, subindex: +, rw: + -> Confirm segmented transfer
		index = 0x1234
		subindex = 0x11
		d = struct.pack("<BHBL", 0x40, index, subindex, 0x00000000)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x41, index, subindex, 0x00000008))
		
		# Segment: Wrong toggle bit -> Abort
		d = struct.pack("<B7s", 0x70, b"\x00\x00\x00\x00\x00\x00\x00")
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, index, subindex, 0x05030000))
		
		#### Test step
		# Initiate: index: +, subindex: +, rw: + -> Confirm segmented transfer
		index = 0x1234
		subindex = 0x11
		d = struct.pack("<BHBL", 0x40, index, subindex, 0x00000000)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x41, index, subindex, 0x00000008))
		
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
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, index, subindex, 0x05030000))
		
		#### Test step
		# Initiate: index: +, subindex: +, rw: + -> Confirm segmented transfer
		index = 0x1234
		subindex = 0x11
		d = struct.pack("<BHBL", 0x40, index, subindex, 0x00000000)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x41, index, subindex, 0x00000008))
		
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
