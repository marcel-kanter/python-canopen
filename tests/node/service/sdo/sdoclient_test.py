import unittest
import sys
import time
import struct
import threading
import can

from canopen import Node, Network
from canopen.objectdictionary import ObjectDictionary, Record, Variable, UNICODE_STRING, UNSIGNED32
from canopen.node.service.sdo import SDOClient


class Vehicle_Download(threading.Thread):
	def __init__(self, testcase, bus):
		threading.Thread.__init__(self, daemon = True)
		self._testcase = testcase
		self._bus = bus
		self._barrier = threading.Barrier(2)
	
	def sync(self, timeout = None):
		self._barrier.wait(timeout)
	
	def run(self):
		try:
			network = Network()
			dictionary = ObjectDictionary()
			dictionary.add(Record("rec", 0x1234, 0x00))
			dictionary["rec"].add(Variable("unicode", 0x1234, 0x0B, UNICODE_STRING, "rw"))
			dictionary.add(Variable("var", 0x5678, 0x00, UNSIGNED32, "rw"))
			node = Node("a", 1, dictionary)
			examinee = SDOClient(node)
			
			network.attach(self._bus)
			node.attach(network)
			examinee.attach()
			
			#### Test step: download, expedited transfer, abort
			self.sync(1)
			
			index = 0x5678
			subindex = 0x00
			value = 0x12345678
			try:
				examinee.download(index, subindex, value)
			except:
				pass
			else:
				assert(False)
			
			#### Test step: download, expedited transfer, wrong index in initiate response
			self.sync(1)
			
			index = 0x5678
			subindex = 0x00
			value = 0x12345678
			try:
				examinee.download(index, subindex, value)
			except:
				pass
			else:
				assert(False)
			
			#### Test step: download, expedited transfer, timeout
			self.sync(1)
			
			index = 0x5678
			subindex = 0x00
			value = 0x12345678
			try:
				examinee.download(index, subindex, value)
			except TimeoutError:
				pass
			else:
				assert(False)
			
			#### Test step: download, expedited transfer
			self.sync(3) # Sleep time of test + sync time
			
			index = 0x5678
			subindex = 0x00
			value = 0x12345678
			examinee.download(index, subindex, value)
			
			#### Test step: download, segmented transfer, toggle bit error
			self.sync(1)
			
			index = 0x1234
			subindex = 0x0B
			value = "123456"
			try:
				examinee.download(index, subindex, value)
			except:
				pass
			else:
				assert(False)
			
			#### Test step: download, segmented transfer only one segment
			self.sync(1)
			
			index = 0x1234
			subindex = 0x0B
			value = "123"
			examinee.download(index, subindex, value)
			
			#### Test step: download, segmented transfer
			self.sync(1)
			
			index = 0x1234
			subindex = 0x0B
			value = "123456789ABCDE"
			examinee.download(index, subindex, value)
			
			examinee.detach()
			
			#### Start of tests with extended frames
			
			examinee.attach((1 << 29) | (0x1580 + node.id), (1 << 29) | (0x1600 + node.id))
			
			self.sync(1)
			
			#### Test step: download, expedited transfer, abort
			index = 0x5678
			subindex = 0x00
			value = 0x12345678
			try:
				examinee.download(index, subindex, value)
			except:
				pass
			else:
				assert(False)
			
			self.sync(1)
			
			#### Test step: download, segmented transfer, toggle bit error
			index = 0x1234
			subindex = 0x0B
			value = "123456"
			try:
				examinee.download(index, subindex, value)
			except:
				pass
			else:
				assert(False)
			
			self.sync(1)
			
			#### Test step: download, expedited transfer
			index = 0x5678
			subindex = 0x00
			value = 0x12345678
			examinee.download(index, subindex, value)
			
			self.sync(1)
			
			#### Test step: download, segmented transfer
			index = 0x1234
			subindex = 0x0B
			value = "123456789ABCDE"
			examinee.download(index, subindex, value)
			
			examinee.detach()
			
			node.detach()
			network.detach()
		except AssertionError:
			self._testcase.result.addFailure(self._testcase, sys.exc_info())
		except:
			self._testcase.result.addError(self._testcase, sys.exc_info())


class Vehicle_Upload(threading.Thread):
	def __init__(self, testcase, bus):
		threading.Thread.__init__(self, daemon = True)
		self._testcase = testcase
		self._bus = bus
		self._barrier = threading.Barrier(2)
	
	def sync(self, timeout = None):
		self._barrier.wait(timeout)
	
	def run(self):
		try:
			network = Network()
			dictionary = ObjectDictionary()
			dictionary.add(Record("rec", 0x1234, 0x00))
			dictionary["rec"].add(Variable("unicode", 0x1234, 0x0B, UNICODE_STRING, "rw"))
			dictionary.add(Variable("var", 0x5678, 0x00, UNSIGNED32, "rw"))
			node = Node("a", 1, dictionary)
			examinee = SDOClient(node)
			
			network.attach(self._bus)
			node.attach(network)
			examinee.attach()
			
			self.sync(1)
			
			#### Test step: Upload, expedited transfer, only one valid byte sent
			index = 0x5678
			subindex = 0x00
			# An exception should be raised
			try:
				value = examinee.upload(index, subindex)
			except:
				pass
			else:
				assert(False)
			
			self.sync(1)
			
			#### Test step: Upload, expedited transfer, abort
			index = 0x5678
			subindex = 0x00
			# An exception should be raised
			try:
				value = examinee.upload(index, subindex)
			except:
				pass
			else:
				assert(False)
			
			self.sync(1)
			
			#### Test step: Upload, expedited transfer, wrong index in initiate response
			index = 0x5678
			subindex = 0x00
			# An exception should be raised
			try:
				value = examinee.upload(index, subindex)
			except:
				pass
			else:
				assert(False)
			
			self.sync(1)
			
			#### Test step: Upload, expedited transfer, timeout
			index = 0x5678
			subindex = 0x00
			# An exception should be raised
			try:
				value = examinee.upload(index, subindex)
			except TimeoutError:
				pass
			else:
				assert(False)
			
			self.sync(3) # sleep time + sync time
			
			#### Test step: Upload, expedited transfer
			index = 0x5678
			subindex = 0x00
			value = examinee.upload(index, subindex)
			
			assert(value == 1234)
			
			self.sync(1)
			
			#### Test step: Upload, segmented transfer, size not indicated
			index = 0x1234
			subindex = 0x0B
			# An exception should be raised
			try:
				value = examinee.upload(index, subindex)
			except:
				pass
			else:
				assert(False)
			
			self.sync(1)
			
			#### Test step: Upload, segmented transfer, toggle bit error
			index = 0x1234
			subindex = 0x0B
			# An exception should be raised
			try:
				value = examinee.upload(index, subindex)
			except:
				pass
			else:
				assert(False)
			
			self.sync(1)
			
			#### Test step: Upload, segmented transfer, size does not match indicated size
			index = 0x1234
			subindex = 0x0B
			# An exception should be raised
			try:
				value = examinee.upload(index, subindex)
			except:
				pass
			else:
				assert(False)
			
			self.sync(1)
			
			#### Test step: Upload, segmented transfer
			index = 0x1234
			subindex = 0x0B
			value = examinee.upload(index, subindex)
			
			assert(value == "123456")
			
			examinee.detach()
			
			#### Start of tests with extended frames
			examinee.attach((1 << 29) | (0x1580 + node.id), (1 << 29) | (0x1600 + node.id))
			
			self.sync(1)
			
			#### Test step: Upload, expedited transfer, abort
			index = 0x5678
			subindex = 0x00
			# An exception should be raised
			try:
				value = examinee.upload(index, subindex)
			except:
				pass
			else:
				assert(False)
			
			self.sync(1)
			
			#### Test step: Upload, expedited transfer
			index = 0x5678
			subindex = 0x00
			value = examinee.upload(index, subindex)
			
			assert(value == 1234)
			
			self.sync(1)
			
			#### Test step: Upload, segmented transfer
			index = 0x1234
			subindex = 0x0B
			value = examinee.upload(index, subindex)
			
			assert(value == "123456")
			
			examinee.detach()
			
			node.detach()
			network.detach()
		except AssertionError:
			self._testcase.result.addFailure(self._testcase, sys.exc_info())
		except:
			self._testcase.result.addError(self._testcase, sys.exc_info())


class SDOClientTestCase(unittest.TestCase):
	def run(self, result = None):
		if result == None:
			self.result = self.defaultTestResult()
		else:
			self.result = result
		
		unittest.TestCase.run(self, self.result)
		
		return self.result
	
	def test_init(self):
		dictionary = ObjectDictionary()
		node = Node("n", 1, dictionary)
		examinee = SDOClient(node, timeout = 2)
		
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
		examinee = SDOClient(node)
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
		
		examinee.attach((1 << 29) | (0x580 + node.id), (1 << 29) | (0x600 + node.id))
		self.assertTrue(examinee.is_attached())
		
		examinee.detach()
		self.assertFalse(examinee.is_attached())
		
		node.detach()
	
	def test_on_response(self):
		bus1 = can.Bus(interface = "virtual", channel = 0)
		bus2 = can.Bus(interface = "virtual", channel = 0)
		dictionary = ObjectDictionary()
		node = Node("1", 0x01, dictionary)
		examinee = SDOClient(node)
		network = Network()
		
		network.attach(bus1)
		node.attach(network)
		examinee.attach()
		
		# Wrong data length -> Ignored by SDOClient
		message_send = can.Message(arbitration_id = 0x581, is_extended_id = False, data = b"\x00")
		bus2.send(message_send)
		time.sleep(0.001)
		
		# Segment upload response without transfer -> abort
		d = struct.pack("<BHB4s", 0x00, 0x0000, 0x00, b"\x00\x00\x00\x00")
		message = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, 0x0000, 0x00, 0x05040001))
		
		# Segment download response without transfer -> abort
		d = struct.pack("<BHB4s", 0x20, 0x0000, 0x00, b"\x00\x00\x00\x00")
		message = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, 0x0000, 0x00, 0x05040001))
		
		# initiate upload response without transfer -> abort
		d = struct.pack("<BHB4s", 0x40, 0x0000, 0x00, b"\x00\x00\x00\x00")
		message = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, 0x0000, 0x00, 0x05040001))
		
		# initiate download response without transfer -> abort
		d = struct.pack("<BHB4s", 0x60, 0x0000, 0x00, b"\x00\x00\x00\x00")
		message = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, 0x0000, 0x00, 0x05040001))
		
		# Abort transfer -> No message
		d = struct.pack("<BHB4s", 0x80, 0x0000, 0x00, b"\x00\x00\x00\x00")
		message = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message)
		time.sleep(0.001)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv, None)
		
		# Block download response -> Not implemented and thus abort
		d = struct.pack("<BHB4s", 0xA0, 0x0000, 0x00, b"\x00\x00\x00\x00")
		message = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, 0x0000, 0x00, 0x05040001))
		
		# Block upload response -> Not implemented and thus abort
		d = struct.pack("<BHB4s", 0xC0, 0x0000, 0x00, b"\x00\x00\x00\x00")
		message = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, 0x0000, 0x00, 0x05040001))
		
		# Network indication response -> Not implemented and thus abort
		message = can.Message(arbitration_id = 0x581, is_extended_id = False, data = b"\xE0\x00\x00\x00\x00\x00\x00\x00")
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, 0x0000, 0x00, 0x05040001))
		
		examinee.detach()
		node.detach()
		network.detach()
		bus1.shutdown()
		bus2.shutdown()
	
	def test_download(self):
		bus1 = can.ThreadSafeBus(interface = "virtual", channel = 0)
		bus2 = can.ThreadSafeBus(interface = "virtual", channel = 0)
		
		vehicle = Vehicle_Download(self, bus1)
		vehicle.start()
		
		#### Test step: download, expedited transfer, abort
		vehicle.sync(1)
		
		index = 0x5678
		subindex = 0x00
		value = 0x12345678
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x23, index, subindex, value))
		
		d = struct.pack("<BHBL", 0x80, index, subindex, 0x05040000)
		message_send = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message_send)
		
		#### Test step: download, expedited transfer, wrong index in initiate response
		vehicle.sync(1)
		
		index = 0x5678
		subindex = 0x00
		value = 0x12345678
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x23, index, subindex, value))
		
		d = struct.pack("<BHBL", 0x60, index ^ 0xFF, subindex, 0x00000000)
		message_send = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message_send)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, index ^ 0xFF, subindex, 0x08000000))
		
		#### Test step: download, expedited transfer, timeout
		vehicle.sync(1)
		
		index = 0x5678
		subindex = 0x00
		value = 0x12345678
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x23, index, subindex, value))
		
		time.sleep(2)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, index, subindex, 0x05040000))
		
		#### Test step: download, expedited transfer
		vehicle.sync(1)
		
		index = 0x5678
		subindex = 0x00
		value = 0x12345678
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x23, index, subindex, value))
		
		d = struct.pack("<BHBL", 0x60, index, subindex, 0x00000000)
		message_send = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message_send)
		
		#### Test step: download, segmented transfer, toggle bit error
		vehicle.sync(1)
		
		index = 0x1234
		subindex = 0x0B
		value = "123456"
		
		# Initiate
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x21, index, subindex, len(value) * 2))
		
		d = struct.pack("<BHBL", 0x60, index, subindex, 0x00000000)
		message_send = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message_send)
		
		# First segment
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<B7s", 0x00, b"\x31\x00\x32\x00\x33\x00\x34"))
		
		d = struct.pack("<B7s", 0x30, b"\x00\x00\x00\x00\x00\x00\x00")
		message_send = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message_send)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, index, subindex, 0x05030000))
		
		#### Test step: download, segmented transfer, only one segment
		vehicle.sync(1)
		
		index = 0x1234
		subindex = 0x0B
		value = "123"
		
		# Initiate
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x21, index, subindex, len(value) * 2))
		
		d = struct.pack("<BHBL", 0x60, index, subindex, 0x00000000)
		message_send = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message_send)
		
		# First segment and last segment
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<B7s", 0x03, b"\x31\x00\x32\x00\x33\x00\x00"))
		
		d = struct.pack("<B7s", 0x20, b"\x00\x00\x00\x00\x00\x00\x00")
		message_send = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message_send)
		
		#### Test step: download, segmented transfer
		vehicle.sync(1)
		
		index = 0x1234
		subindex = 0x0B
		value = "123456789ABCDE"
		
		# Initiate
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x21, index, subindex, len(value) * 2))
		
		d = struct.pack("<BHBL", 0x60, index, subindex, 0x00000000)
		message_send = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message_send)
		
		# First segment
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<B7s", 0x00, b"\x31\x00\x32\x00\x33\x00\x34"))
		
		d = struct.pack("<B7s", 0x20, b"\x00\x00\x00\x00\x00\x00\x00")
		message_send = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message_send)
		
		# Second segment
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<B7s", 0x10, b"\x00\x35\x00\x36\x00\x37\x00"))
		
		d = struct.pack("<B7s", 0x30, b"\x00\x00\x00\x00\x00\x00\x00")
		message_send = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message_send)
		
		# Third segment
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<B7s", 0x00, b"\x38\x00\x39\x00\x41\x00\x42"))
		
		d = struct.pack("<B7s", 0x20, b"\x00\x00\x00\x00\x00\x00\x00")
		message_send = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message_send)
		
		# Fourth and last segment
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<B7s", 0x11, b"\x00\x43\x00\x44\x00\x45\x00"))
		
		d = struct.pack("<B7s", 0x30, b"\x00\x00\x00\x00\x00\x00\x00")
		message_send = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message_send)
				
		#### Start of tests with extended frames
		
		#### Test step: download, expedited transfer, abort
		vehicle.sync(1)
		
		index = 0x5678
		subindex = 0x00
		value = 0x12345678
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x1601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, True)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x23, index, subindex, value))
		
		d = struct.pack("<BHBL", 0x80, index, subindex, 0x05040000)
		message_send = can.Message(arbitration_id = 0x1581, is_extended_id = True, data = d)
		bus2.send(message_send)
		
		vehicle.sync(1)
		
		#### Test step: download, segmented transfer, toggle bit error
		index = 0x1234
		subindex = 0x0B
		value = "123456"
		
		# Initiate
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x1601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, True)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x21, index, subindex, len(value) * 2))
		
		d = struct.pack("<BHBL", 0x60, index, subindex, 0x00000000)
		message_send = can.Message(arbitration_id = 0x1581, is_extended_id = True, data = d)
		bus2.send(message_send)
		
		# First segment
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x1601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, True)
		self.assertEqual(message_recv.data, struct.pack("<B7s", 0x00, b"\x31\x00\x32\x00\x33\x00\x34"))
		
		d = struct.pack("<B7s", 0x30, b"\x00\x00\x00\x00\x00\x00\x00")
		message_send = can.Message(arbitration_id = 0x1581, is_extended_id = True, data = d)
		bus2.send(message_send)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x1601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, True)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, index, subindex, 0x05030000))
		
		vehicle.sync(1)
		
		#### Test step: download, expedited transfer
		index = 0x5678
		subindex = 0x00
		value = 0x12345678
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x1601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, True)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x23, index, subindex, value))
		
		d = struct.pack("<BHBL", 0x60, index, subindex, 0x00000000)
		message_send = can.Message(arbitration_id = 0x1581, is_extended_id = True, data = d)
		bus2.send(message_send)
		
		vehicle.sync(1)
		
		#### Test step: download, segmented transfer
		index = 0x1234
		subindex = 0x0B
		value = "123456789ABCDE"
		
		# Initiate
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x1601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, True)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x21, index, subindex, len(value) * 2))
		
		d = struct.pack("<BHBL", 0x60, index, subindex, 0x00000000)
		message_send = can.Message(arbitration_id = 0x1581, is_extended_id = True, data = d)
		bus2.send(message_send)
		
		# First segment
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x1601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, True)
		self.assertEqual(message_recv.data, struct.pack("<B7s", 0x00, b"\x31\x00\x32\x00\x33\x00\x34"))
		
		d = struct.pack("<B7s", 0x20, b"\x00\x00\x00\x00\x00\x00\x00")
		message_send = can.Message(arbitration_id = 0x1581, is_extended_id = True, data = d)
		bus2.send(message_send)
		
		# Second segment
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x1601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, True)
		self.assertEqual(message_recv.data, struct.pack("<B7s", 0x10, b"\x00\x35\x00\x36\x00\x37\x00"))
		
		d = struct.pack("<B7s", 0x30, b"\x00\x00\x00\x00\x00\x00\x00")
		message_send = can.Message(arbitration_id = 0x1581, is_extended_id = True, data = d)
		bus2.send(message_send)
		
		# Third segment
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x1601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, True)
		self.assertEqual(message_recv.data, struct.pack("<B7s", 0x00, b"\x38\x00\x39\x00\x41\x00\x42"))
		
		d = struct.pack("<B7s", 0x20, b"\x00\x00\x00\x00\x00\x00\x00")
		message_send = can.Message(arbitration_id = 0x1581, is_extended_id = True, data = d)
		bus2.send(message_send)
		
		# Fourth and last segment
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x1601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, True)
		self.assertEqual(message_recv.data, struct.pack("<B7s", 0x11, b"\x00\x43\x00\x44\x00\x45\x00"))
		
		d = struct.pack("<B7s", 0x30, b"\x00\x00\x00\x00\x00\x00\x00")
		message_send = can.Message(arbitration_id = 0x1581, is_extended_id = True, data = d)
		bus2.send(message_send)
		
		vehicle.join(1)
		
		bus1.shutdown()
		bus2.shutdown()
	
	def test_upload(self):
		bus1 = can.ThreadSafeBus(interface = "virtual", channel = 0)
		bus2 = can.ThreadSafeBus(interface = "virtual", channel = 0)
		
		vehicle = Vehicle_Upload(self, bus1)
		vehicle.start()
		
		vehicle.sync(1)
		
		#### Test step: Upload, expedited transfer, only one valid byte sent
		index = 0x5678
		subindex = 0x00
		value = 1234
		# Initiation
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x40, index, subindex, 0x00000000))
		
		d = struct.pack("<BHBL", 0x4F, index, subindex, value)
		message_send = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message_send)
		time.sleep(0.001)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, index, subindex, 0x06070010))
		
		vehicle.sync(1)
		
		#### Test step: Upload, expedited transfer, abort
		index = 0x5678
		subindex = 0x00
		value = 1234
		# Initiation
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x40, index, subindex, 0x00000000))
		
		d = struct.pack("<BHBL", 0x80, index, subindex, 0x05040000)
		message_send = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message_send)
		time.sleep(0.001)
		
		vehicle.sync(1)
		
		#### Test step: Upload, expedited transfer, wrong index in initiate response
		index = 0x5678
		subindex = 0x00
		value = 1234
		# Initiation
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x40, index, subindex, 0x00000000))
		
		d = struct.pack("<BHBL", 0x42, index ^ 0xFF, subindex, value)
		message_send = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message_send)
		time.sleep(0.001)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, index ^ 0xFF, subindex, 0x08000000))
		
		vehicle.sync(1)
		
		#### Test step: Upload, expedited transfer, timeout
		index = 0x5678
		subindex = 0x00
		value = 1234
		# Initiation
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x40, index, subindex, 0x00000000))
		
		time.sleep(2)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, index, subindex, 0x05040000))
		
		vehicle.sync(1)
		
		#### Test step: Upload, expedited transfer
		index = 0x5678
		subindex = 0x00
		value = 1234
		# Initiation
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x40, index, subindex, 0x00000000))
		
		d = struct.pack("<BHBL", 0x42, index, subindex, value)
		message_send = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message_send)
		time.sleep(0.001)
		
		vehicle.sync(1)
		
		#### Test step: Upload, segmented transfer, size not indicated
		index = 0x1234
		subindex = 0x0B
		value = "123456"
		# Initiation
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x40, index, subindex, 0x00000000))
		
		d = struct.pack("<BHBL", 0x40, index, subindex, len(value) * 2)
		message_send = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message_send)
		time.sleep(0.001)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, index, subindex, 0x05040001))
		
		vehicle.sync(1)
		
		#### Test step: Upload, segmented transfer, toggle bit error
		index = 0x1234
		subindex = 0x0B
		value = "123456"
		# Initiation
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x40, index, subindex, 0x00000000))
		
		d = struct.pack("<BHBL", 0x41, index, subindex, len(value) * 2)
		message_send = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message_send)
		time.sleep(0.001)
		
		# First segment
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<B7s", 0x60, b"\x00\x00\x00\x00\x00\x00\x00"))
		
		d = struct.pack("<B7s", 0x10, b"\x31\x00\x32\x00\x33\x00\x34")
		message_send = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message_send)
		time.sleep(0.001)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, index, subindex, 0x05030000))
		
		vehicle.sync(1)
		
		#### Test step: Upload, segmented transfer, size does not match indicated size
		index = 0x1234
		subindex = 0x0B
		value = "123456"
		# Initiation
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x40, index, subindex, 0x00000000))
		
		d = struct.pack("<BHBL", 0x41, index, subindex, len(value))
		message_send = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message_send)
		time.sleep(0.001)
		
		# First segment
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<B7s", 0x60, b"\x00\x00\x00\x00\x00\x00\x00"))
		
		d = struct.pack("<B7s", 0x00, b"\x31\x00\x32\x00\x33\x00\x34")
		message_send = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message_send)
		time.sleep(0.001)
		
		# Second and last segment
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<B7s", 0x70, b"\x00\x00\x00\x00\x00\x00\x00"))
		
		d = struct.pack("<B7s", 0x15, b"\x00\x35\x00\x36\x00\x00\x00")
		message_send = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message_send)
		time.sleep(0.001)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, index, subindex, 0x06070010))
		
		vehicle.sync(1)
		
		#### Test step: Upload, segmented transfer
		index = 0x1234
		subindex = 0x0B
		value = "123456"
		# Initiation
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x40, index, subindex, 0x00000000))
		
		d = struct.pack("<BHBL", 0x41, index, subindex, len(value) * 2)
		message_send = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message_send)
		time.sleep(0.001)
		
		# First segment
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<B7s", 0x60, b"\x00\x00\x00\x00\x00\x00\x00"))
		
		d = struct.pack("<B7s", 0x00, b"\x31\x00\x32\x00\x33\x00\x34")
		message_send = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message_send)
		time.sleep(0.001)
		
		# Second and last segment
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<B7s", 0x70, b"\x00\x00\x00\x00\x00\x00\x00"))
		
		d = struct.pack("<B7s", 0x15, b"\x00\x35\x00\x36\x00\x00\x00")
		message_send = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message_send)
		time.sleep(0.001)
		
		#### Start of tests with extended frames
		
		vehicle.sync(1)
		
		#### Test step: Upload, expedited transfer, abort
		index = 0x5678
		subindex = 0x00
		value = 1234
		# Initiation
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x1601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, True)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x40, index, subindex, 0x00000000))
		
		d = struct.pack("<BHBL", 0x80, index, subindex, 0x05040000)
		message_send = can.Message(arbitration_id = 0x1581, is_extended_id = True, data = d)
		bus2.send(message_send)
		time.sleep(0.001)
		
		vehicle.sync(1)
		
		#### Test step: Upload, expedited transfer
		index = 0x5678
		subindex = 0x00
		value = 1234
		# Initiation
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x1601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, True)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x40, index, subindex, 0x00000000))
		
		d = struct.pack("<BHBL", 0x42, index, subindex, value)
		message_send = can.Message(arbitration_id = 0x1581, is_extended_id = True, data = d)
		bus2.send(message_send)
		time.sleep(0.001)
		
		vehicle.sync(1)
		
		#### Test step: Upload, segmented transfer
		index = 0x1234
		subindex = 0x0B
		value = "123456"
		# Initiation
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x1601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, True)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x40, index, subindex, 0x00000000))
		
		d = struct.pack("<BHBL", 0x41, index, subindex, len(value) * 2)
		message_send = can.Message(arbitration_id = 0x1581, is_extended_id = True, data = d)
		bus2.send(message_send)
		time.sleep(0.001)
		
		# First segment
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x1601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, True)
		self.assertEqual(message_recv.data, struct.pack("<B7s", 0x60, b"\x00\x00\x00\x00\x00\x00\x00"))
		
		d = struct.pack("<B7s", 0x00, b"\x31\x00\x32\x00\x33\x00\x34")
		message_send = can.Message(arbitration_id = 0x1581, is_extended_id = True, data = d)
		bus2.send(message_send)
		time.sleep(0.001)
		
		# Second and last segment
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x1601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.is_extended_id, True)
		self.assertEqual(message_recv.data, struct.pack("<B7s", 0x70, b"\x00\x00\x00\x00\x00\x00\x00"))
		
		d = struct.pack("<B7s", 0x15, b"\x00\x35\x00\x36\x00\x00\x00")
		message_send = can.Message(arbitration_id = 0x1581, is_extended_id = True, data = d)
		bus2.send(message_send)
		time.sleep(0.001)
		
		vehicle.join(1)
		
		bus1.shutdown()
		bus2.shutdown()


if __name__ == "__main__":
	unittest.main()
