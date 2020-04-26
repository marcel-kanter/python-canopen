import unittest
import time
import struct
import can

from canopen import Node, Network
from canopen.objectdictionary import ObjectDictionary, Record, Variable, BOOLEAN, INTEGER8, INTEGER16, INTEGER32, UNSIGNED8, UNSIGNED16, UNSIGNED32, DOMAIN, INTEGER24, REAL64, INTEGER40
from canopen.sdo.abortcodes import NO_ERROR
from canopen.node.service.sdo import SDOServer
from tests.node.inspectionnode import InspectionNode
import canopen


class SDOServerTestCase(unittest.TestCase):
	def test_init(self):
		dictionary = ObjectDictionary()
		node = Node("n", 1, dictionary)
		examinee = SDOServer(node, timeout = 2)
		
		examinee.timeout = None
		self.assertEqual(examinee.timeout, None)
		
		examinee.timeout = 1.0
		self.assertEqual(examinee.timeout, 1.0)
		
		with self.assertRaises(ValueError):
			examinee.timeout = 0
		
		with self.assertRaises(ValueError):
			examinee.timeout = -1  
	
	def test_attach_detach(self):
		dictionary = ObjectDictionary()
		node = Node("n", 1, dictionary)
		examinee = SDOServer(node)
		network = Network()
		
		node.attach(network)
		
		with self.assertRaises(RuntimeError):
			examinee.detach()
		
		examinee.attach()
		self.assertTrue(examinee.is_attached())
		
		examinee.attach()
		self.assertTrue(examinee.is_attached())
		
		test_data = [-1, 0x100000000]
		for value in test_data:
			with self.subTest(value = value):
				with self.assertRaises(ValueError):
					examinee.attach(value, 0)
				with self.assertRaises(ValueError):
					examinee.attach(0, value)
		
		examinee.attach((1 << 29) | (0x600 + node.id), (1 << 29) | (0x580 + node.id))
		self.assertTrue(examinee.is_attached())
		
		examinee.detach()
		self.assertFalse(examinee.is_attached())
		
		node.detach()
	
	def test_request(self):
		bus1 = can.Bus(interface = "virtual", channel = 0)
		bus2 = can.Bus(interface = "virtual", channel = 0)
		network = Network()
		dictionary = ObjectDictionary()
		node = Node("1", 0x01, dictionary)
		examinee = SDOServer(node)
		
		network.attach(bus1)
		node.attach(network)
		examinee.attach()
		
		# Wrong data length -> Ignored by SDOServer
		message_send = can.Message(arbitration_id = 0x601, is_extended_id = False, data = b"\x00")
		bus2.send(message_send)
		
		message_recv = bus2.recv(0.5)
		self.assertEqual(message_recv, None)
		
		# Abort transfer -> No response
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = b"\x80\x00\x00\x00\x00\x00\x00\x00")
		bus2.send(message)
		
		message_recv = bus2.recv(0.5)
		self.assertEqual(message_recv, None)

		# Block upload: Not implemented and disabled -> No response
		examinee.disable()
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = b"\xA0\x00\x00\x00\x00\x00\x00\x00")
		bus2.send(message)
		
		message_recv = bus2.recv(0.5)
		self.assertEqual(message_recv, None)
		examinee.enable()
		
		# Block upload -> Not implemented and thus the response is an abort
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = b"\xA0\x00\x00\x00\x00\x00\x00\x00")
		bus2.send(message)
		
		message_recv = bus2.recv(0.5)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, b"\x80\x00\x00\x00\x01\x00\x04\x05")
		
		# Block download: Not implemented and disabled -> No response
		examinee.disable()
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = b"\xC0\x00\x00\x00\x00\x00\x00\x00")
		bus2.send(message)
		
		message_recv = bus2.recv(0.5)
		self.assertEqual(message_recv, None)
		examinee.enable()
		
		# Block download -> Not implemented and thus the response is an abort
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = b"\xC0\x00\x00\x00\x00\x00\x00\x00")
		bus2.send(message)
		
		message_recv = bus2.recv(0.5)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, b"\x80\x00\x00\x00\x01\x00\x04\x05")
		
		# Network indication: Not implemented and disabled -> No response
		examinee.disable()
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = b"\xE0\x00\x00\x00\x00\x00\x00\x00")
		bus2.send(message)
		
		message_recv = bus2.recv(0.5)
		self.assertEqual(message_recv, None)
		examinee.enable()
		
		# Network indication -> Not implemented and thus the response is an abort
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = b"\xE0\x00\x00\x00\x00\x00\x00\x00")
		bus2.send(message)
		
		message_recv = bus2.recv(0.5)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, b"\x80\x00\x00\x00\x01\x00\x04\x05")
		
		examinee.detach()
		node.detach()
		network.detach()
		bus1.shutdown()
		bus2.shutdown()
	
	def test_download(self):
		bus1 = can.Bus(interface = "virtual", channel = 0)
		bus2 = can.Bus(interface = "virtual", channel = 0)
		dictionary = ObjectDictionary()
		dictionary.add(Record("rec", 0x1234, 0x00))
		dictionary["rec"].add(Variable("boolean", 0x1234, 0x01, BOOLEAN, "rw"))
		dictionary["rec"].add(Variable("integer8", 0x1234, 0x02, INTEGER8, "rw"))
		dictionary["rec"].add(Variable("integer16", 0x1234, 0x03, INTEGER16, "rw"))
		dictionary["rec"].add(Variable("integer32", 0x1234, 0x04, INTEGER32, "rw"))
		dictionary["rec"].add(Variable("unsigned8", 0x1234, 0x05, UNSIGNED8, "ro"))
		dictionary["rec"].add(Variable("unsigned16", 0x1234, 0x06, UNSIGNED16, "wo"))
		dictionary["rec"].add(Variable("domain", 0x1234, 0x0F, DOMAIN, "rw"))
		dictionary["rec"].add(Variable("integer24", 0x1234, 0x10, INTEGER24, "rw"))
		dictionary["rec"].add(Variable("real64", 0x1234, 0x11, REAL64, "rw"))
		dictionary["rec"].add(Variable("integer40", 0x1234, 0x12, INTEGER40, "rw"))
		dictionary.add(Variable("var", 0x5678, 0x00, UNSIGNED32, "rw"))
		dictionary.add(Variable("const", 0x7777, 0x00, UNSIGNED32, "const"))
		node = InspectionNode("a", 1, dictionary)
		examinee = SDOServer(node)
		network = Network()
		
		network.attach(bus1)
		node.attach(network)
		examinee.attach()
		
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
		# Initiate: index: +, subindex: +, rw: - (const) -> Abort with attempt to write an read only object
		index = 0x7777
		subindex = 0x00
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
		dictionary.add(Variable("var", 0x5678, 0x00, 0x07, "rw"))
		
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
		dictionary["rec"].add(Variable("domain", 0x1234, 0x0F, DOMAIN, "rw"))
		
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
		
		#### Test step: Segmented download with write error in node -> Abort Data cannot be stored in application
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
		
		#### Test step: Segmented download
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
		
		#### Test step: Expedited download, disabled service -> No response
		# Initiate: index: +, subindex: +, rw: +, e = 1 & s = 0 & n = 0 -> No response (disabled service)
		examinee.disable()
		index = 0x5678
		subindex = 0x00
		d = struct.pack("<BHBL", 0x22, index, subindex, 0x87654321)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(0.5)
		self.assertEqual(message_recv, None)
		
		# check previously written value
		self.assertEqual(node[0x5678].value, 0x12345678)
		examinee.enable()
		
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
		d = struct.pack("<BHBL", 0x2B, index, subindex, 0x12345678)
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
		
		#### Test detach during ongoing segmented transfer
		
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
		
		examinee.detach()
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x581)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data,struct.pack("<BHBL", 0x80, index, subindex, NO_ERROR))
		
		self.assertFalse(examinee.is_attached())
		
		#### Start of tests with extended frames
		
		examinee.attach((1 << 29) | (0x1600 + node.id), (1 << 29) | (0x1580 + node.id))
		
		#### Test step
		# Initiate: index: - -> Abort with index unknown
		index = 0x0000
		subindex = 0x00
		d = struct.pack("<BHBL", 0x20, index, subindex, 0x00000000)
		message = can.Message(arbitration_id = 0x1601, is_extended_id = True, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x1581)
		self.assertEqual(message_recv.is_extended_id, True)
		self.assertEqual(message_recv.data,struct.pack("<BHBL", 0x80, index, subindex, 0x06020000))
		
		#### Test step: Segmented download
		# Initiate: e = 0 & s = 1 & size in data -> Confirm
		index = 0x5678
		subindex = 0x00
		d = struct.pack("<BHBL", 0x21, index, subindex, 0x00000004)
		message = can.Message(arbitration_id = 0x1601, is_extended_id = True, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x1581)
		self.assertEqual(message_recv.is_extended_id, True)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x60, index, subindex, 0x00000000))
		
		# Segment: Correct toggle bit -> Confirm
		d = struct.pack("<B7s", 0x0A, b"\x11\x22\x00\x00\x00\x00\x00")
		message = can.Message(arbitration_id = 0x1601, is_extended_id = True, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x1581)
		self.assertEqual(message_recv.is_extended_id, True)
		self.assertEqual(message_recv.data, struct.pack("<B7s", 0x20, b"\x00\x00\x00\x00\x00\x00\x00"))
		
		# Segment: Correct toggle bit, Close transfer / Last segment -> Confirm
		d = struct.pack("<B7s", 0x1B, b"\x33\x44\x00\x00\x00\x00\x00")
		message = can.Message(arbitration_id = 0x1601, is_extended_id = True, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x1581)
		self.assertEqual(message_recv.is_extended_id, True)
		self.assertEqual(message_recv.data, struct.pack("<B7s", 0x30, b"\x00\x00\x00\x00\x00\x00\x00"))
		
		#### Test step
		# Initiate: index: +, subindex: +, rw: +, e = 1 & s = 1 & n = 0 -> Confirm on variable with 4 bytes length or less
		index = 0x1234
		subindex = 0x04
		d = struct.pack("<BHBL", 0x23, index, subindex, 0x12345678)
		message = can.Message(arbitration_id = 0x1601, is_extended_id = True, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x1581)
		self.assertEqual(message_recv.is_extended_id, True)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x60, index, subindex, 0x00000000))
		
		self.assertEqual(node[0x1234][0x04].value, 0x12345678)
		
		examinee.detach()
		node.detach()
		network.detach()
		bus1.shutdown()
		bus2.shutdown()
	
	def test_upload(self):
		bus1 = can.Bus(interface = "virtual", channel = 0)
		bus2 = can.Bus(interface = "virtual", channel = 0)
		network = Network()
		dictionary = ObjectDictionary()
		dictionary.add(Record("rec", 0x1234, 0x00))
		dictionary["rec"].add(Variable("boolean", 0x1234, 0x01, BOOLEAN, "rw"))
		dictionary["rec"].add(Variable("integer8", 0x1234, 0x02, INTEGER8, "rw"))
		dictionary["rec"].add(Variable("integer16", 0x1234, 0x03, INTEGER16, "rw"))
		dictionary["rec"].add(Variable("integer32", 0x1234, 0x04, INTEGER32, "rw"))
		dictionary["rec"].add(Variable("unsigned8", 0x1234, 0x05, UNSIGNED8, "ro"))
		dictionary["rec"].add(Variable("unsigned16", 0x1234, 0x06, UNSIGNED16, "wo"))
		dictionary["rec"].add(Variable("domain", 0x1234, 0x0F, DOMAIN, "rw"))
		dictionary["rec"].add(Variable("integer24", 0x1234, 0x10, INTEGER24, "rw"))
		dictionary["rec"].add(Variable("real64", 0x1234, 0x11, REAL64, "rw"))
		dictionary["rec"].add(Variable("integer40", 0x1234, 0x12, INTEGER40, "rw"))
		dictionary.add(Variable("var", 0x5678, 0x00, UNSIGNED32, "rw"))
		node = InspectionNode("a", 1, dictionary)
		examinee = SDOServer(node)
		
		network.attach(bus1)
		node.attach(network)
		examinee.attach()
		
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
		# Initiate: index: +, subindex: +, rw: + -> But service disabled -> No response
		examinee.disable()
		index = 0x5678
		subindex = 0x00
		d = struct.pack("<BHBL", 0x40, index, subindex, 0x00000000)
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(0.5)
		self.assertEqual(message_recv, None)
		examinee.enable()
		
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
		
		examinee.detach()
		
		#### Start of tests with extended frames
		
		examinee.attach((1 << 29) | (0x1600 + node.id), (1 << 29) | (0x1580 + node.id))
		
		#### Test step
		# Initiate: index: - -> Abort with index unknown
		index = 0x0000
		subindex = 0x00
		d = struct.pack("<BHBL", 0x40, index, subindex, 0x00000000)
		message = can.Message(arbitration_id = 0x1601, is_extended_id = True, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x1581)
		self.assertEqual(message_recv.is_extended_id, True)
		self.assertEqual(message_recv.data,struct.pack("<BHBL", 0x80, index, subindex, 0x06020000))
		
		#### Test step
		# Initiate: index: +, subindex: +, rw: + -> Confirm expedited transfer
		index = 0x5678
		subindex = 0x00
		d = struct.pack("<BHBL", 0x40, index, subindex, 0x00000000)
		message = can.Message(arbitration_id = 0x1601, is_extended_id = True, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x1581)
		self.assertEqual(message_recv.is_extended_id, True)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x43, index, subindex, 12345))
		
		#### Test step
		# Initiate: index: +, subindex: +, rw: + -> Confirm segmented transfer
		index = 0x1234
		subindex = 0x11
		d = struct.pack("<BHBL", 0x40, index, subindex, 0x00000000)
		message = can.Message(arbitration_id = 0x1601, is_extended_id = True, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x1581)
		self.assertEqual(message_recv.is_extended_id, True)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x41, index, subindex, 0x00000008))
		
		# Segment: Correct toggle bit -> Data segment
		d = struct.pack("<B7s", 0x60, b"\x00\x00\x00\x00\x00\x00\x00")
		message = can.Message(arbitration_id = 0x1601, is_extended_id = True, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x1581)
		self.assertEqual(message_recv.is_extended_id, True)
		self.assertEqual(message_recv.data, struct.pack("<B7s", 0x00, b"\x00\x00\x00\x00\x00\x00\x00"))
		
		# Segment: Correct toggle bit -> Last segment
		d = struct.pack("<B7s", 0x70, b"\x00\x00\x00\x00\x00\x00\x00")
		message = can.Message(arbitration_id = 0x1601, is_extended_id = True, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x1581)
		self.assertEqual(message_recv.is_extended_id, True)
		self.assertEqual(message_recv.data, struct.pack("<B7s", 0x1D, b"\x00\x00\x00\x00\x00\x00\x00"))
		
		examinee.detach()
		node.detach()
		network.detach()
		bus1.shutdown()
		bus2.shutdown()


if __name__ == "__main__":
	unittest.main()
