import unittest
import time
import struct
import threading
import can
import canopen.objectdictionary
import canopen.node.service


class Vehicle_Download(threading.Thread):
	def __init__(self, bus):
		threading.Thread.__init__(self)
		self._bus = bus
		self._terminate = threading.Event()
	
	def stop(self):
		self._terminate.set()
	
	def run(self):
		network = canopen.Network()
		dictionary = canopen.ObjectDictionary()
		dictionary.append(canopen.objectdictionary.Record("rec", 0x1234))
		dictionary["rec"].append(canopen.objectdictionary.Variable("unicode", 0x1234, 0x0B, canopen.objectdictionary.UNICODE_STRING, "rw"))
		dictionary.append(canopen.objectdictionary.Variable("var", 0x5678, 0x00, canopen.objectdictionary.UNSIGNED32, "rw"))
		node = canopen.Node("a", 1, dictionary)
		examinee = canopen.node.service.SDOClient()
		
		network.attach(self._bus)
		node.attach(network)
		examinee.attach(node)
		
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
		
		#### Test step: download, expedited transfer, wrong index in initiate response
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
		index = 0x5678
		subindex = 0x00
		value = 0x12345678
		try:
			examinee.download(index, subindex, value)
		except:
			pass
		else:
			assert(False)
		
		#### Test step: download, expedited transfer
		index = 0x5678
		subindex = 0x00
		value = 0x12345678
		examinee.download(index, subindex, value)
		
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
		
		#### Test step: download, segmented transfer only one segment
		index = 0x1234
		subindex = 0x0B
		value = "123"
		examinee.download(index, subindex, value)
		
		#### Test step: download, segmented transfer
		index = 0x1234
		subindex = 0x0B
		value = "123456789ABCDE"
		examinee.download(index, subindex, value)
		
		while not self._terminate.is_set():
			self._terminate.wait(0.1)
		
		examinee.detach()
		node.detach()
		network.detach()


class Vehicle_Upload(threading.Thread):
	def __init__(self, bus):
		threading.Thread.__init__(self)
		self._bus = bus
		self._terminate = threading.Event()
	
	def stop(self):
		self._terminate.set()
	
	def run(self):
		network = canopen.Network()
		dictionary = canopen.ObjectDictionary()
		dictionary.append(canopen.objectdictionary.Record("rec", 0x1234))
		dictionary["rec"].append(canopen.objectdictionary.Variable("unicode", 0x1234, 0x0B, canopen.objectdictionary.UNICODE_STRING, "rw"))
		dictionary.append(canopen.objectdictionary.Variable("var", 0x5678, 0x00, canopen.objectdictionary.UNSIGNED32, "rw"))
		node = canopen.Node("a", 1, dictionary)
		examinee = canopen.node.service.SDOClient()
		
		network.attach(self._bus)
		node.attach(network)
		examinee.attach(node)
		
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
		
		#### Test step: Upload, expedited transfer, timeout
		index = 0x5678
		subindex = 0x00
		# An exception should be raised
		try:
			value = examinee.upload(index, subindex)
		except:
			pass
		else:
			assert(False)
		
		#### Test step: Upload, expedited transfer
		index = 0x5678
		subindex = 0x00
		value = examinee.upload(index, subindex)
		
		# TODO: make asserting visible in test case
		assert(value == 1234)
		
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
		
		#### Test step: Upload, segmented transfer
		index = 0x1234
		subindex = 0x0B
		value = examinee.upload(index, subindex)
		
		# TODO: make asserting visible in test case
		assert(value == "123456")
		
		while not self._terminate.is_set():
			self._terminate.wait(0.1)
		
		examinee.detach()
		node.detach()
		network.detach()


class SDOClientTestCase(unittest.TestCase):
	def test_init(self):
		examinee = canopen.node.service.SDOClient(timeout = 2)
		
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
		
		# Segment upload response without transfer -> abort
		d = struct.pack("<BHB4s", 0x00, 0x0000, 0x00, b"\x00\x00\x00\x00")
		message = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, 0x0000, 0x00, 0x05040001))
		
		# Segment download response without transfer -> abort
		d = struct.pack("<BHB4s", 0x20, 0x0000, 0x00, b"\x00\x00\x00\x00")
		message = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, 0x0000, 0x00, 0x05040001))
		
		# initiate upload response without transfer -> abort
		d = struct.pack("<BHB4s", 0x40, 0x0000, 0x00, b"\x00\x00\x00\x00")
		message = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, 0x0000, 0x00, 0x05040001))
		
		# initiate download response without transfer -> abort
		d = struct.pack("<BHB4s", 0x60, 0x0000, 0x00, b"\x00\x00\x00\x00")
		message = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
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
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, 0x0000, 0x00, 0x05040001))
		
		# Block upload response -> Not implemented and thus abort
		d = struct.pack("<BHB4s", 0xC0, 0x0000, 0x00, b"\x00\x00\x00\x00")
		message = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message)
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, 0x0000, 0x00, 0x05040001))
		
		# Network indication response -> Not implemented and thus  abort
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
	
	def test_download(self):
		bus1 = can.Bus(interface = "virtual", channel = 0)
		bus2 = can.Bus(interface = "virtual", channel = 0)
		
		vehicle = Vehicle_Download(bus1)
		vehicle.start()

		#### Test step: download, expedited transfer, abort
		index = 0x5678
		subindex = 0x00
		value = 0x12345678
		
		message_recv = bus2.recv(0.5)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x23, index, subindex, value))
		
		d = struct.pack("<BHBL", 0x80, index, subindex, 0x05040000)
		message_send = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message_send)
		
		#### Test step: download, expedited transfer, wrong index in initiate response
		index = 0x5678
		subindex = 0x00
		value = 0x12345678
		
		message_recv = bus2.recv(0.5)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x23, index, subindex, value))
		
		d = struct.pack("<BHBL", 0x60, index ^ 0xFF, subindex, 0x00000000)
		message_send = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message_send)
		
		message_recv = bus2.recv()
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, index ^ 0xFF, subindex, 0x08000000))
		
		#### Test step: download, expedited transfer, timeout
		index = 0x5678
		subindex = 0x00
		value = 0x12345678
		
		message_recv = bus2.recv(0.5)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x23, index, subindex, value))
		
		time.sleep(2)
		
		message_recv = bus2.recv()
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, index, subindex, 0x05040000))
		
		#### Test step: download, expedited transfer
		index = 0x5678
		subindex = 0x00
		value = 0x12345678
		
		message_recv = bus2.recv(0.5)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x23, index, subindex, value))
		
		d = struct.pack("<BHBL", 0x60, index, subindex, 0x00000000)
		message_send = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message_send)
		
		#### Test step: download, segmented transfer, toggle bit error
		index = 0x1234
		subindex = 0x0B
		value = "123456"
		
		# Initiate
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x21, index, subindex, len(value) * 2))
		
		d = struct.pack("<BHBL", 0x60, index, subindex, 0x00000000)
		message_send = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message_send)
		
		# First segment
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.data, struct.pack("<B7s", 0x00, b"\x31\x00\x32\x00\x33\x00\x34"))
		
		d = struct.pack("<B7s", 0x30, b"\x00\x00\x00\x00\x00\x00\x00")
		message_send = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message_send)

		message_recv = bus2.recv()
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, index, subindex, 0x05030000))
		
		#### Test step: download, segmented transfer, only one segment
		index = 0x1234
		subindex = 0x0B
		value = "123"
		
		# Initiate
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x21, index, subindex, len(value) * 2))
		
		d = struct.pack("<BHBL", 0x60, index, subindex, 0x00000000)
		message_send = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message_send)
		
		# First segment and last segment
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.data, struct.pack("<B7s", 0x03, b"\x31\x00\x32\x00\x33\x00\x00"))
		
		d = struct.pack("<B7s", 0x20, b"\x00\x00\x00\x00\x00\x00\x00")
		message_send = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message_send)
		
		#### Test step: download, segmented transfer
		index = 0x1234
		subindex = 0x0B
		value = "123456789ABCDE"
		
		# Initiate
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x21, index, subindex, len(value) * 2))
		
		d = struct.pack("<BHBL", 0x60, index, subindex, 0x00000000)
		message_send = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message_send)
		
		# First segment
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.data, struct.pack("<B7s", 0x00, b"\x31\x00\x32\x00\x33\x00\x34"))
		
		d = struct.pack("<B7s", 0x20, b"\x00\x00\x00\x00\x00\x00\x00")
		message_send = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message_send)
		
		# Second segment
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.data, struct.pack("<B7s", 0x10, b"\x00\x35\x00\x36\x00\x37\x00"))
		
		d = struct.pack("<B7s", 0x30, b"\x00\x00\x00\x00\x00\x00\x00")
		message_send = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message_send)
		
		# Third segment
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.data, struct.pack("<B7s", 0x00, b"\x38\x00\x39\x00\x41\x00\x42"))
		
		d = struct.pack("<B7s", 0x20, b"\x00\x00\x00\x00\x00\x00\x00")
		message_send = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message_send)
		
		# Fourth and last segment
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.data, struct.pack("<B7s", 0x11, b"\x00\x43\x00\x44\x00\x45\x00"))
		
		d = struct.pack("<B7s", 0x30, b"\x00\x00\x00\x00\x00\x00\x00")
		message_send = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message_send)
		
		self.assertTrue(vehicle.is_alive())
		vehicle.stop()
		vehicle.join()
		
		bus1.shutdown()
		bus2.shutdown()
	
	def test_upload(self):
		bus1 = can.Bus(interface = "virtual", channel = 0)
		bus2 = can.Bus(interface = "virtual", channel = 0)
		
		vehicle = Vehicle_Upload(bus1)
		vehicle.start()
				
		#### Test step: Upload, expedited transfer, only one valid byte sent
		index = 0x5678
		subindex = 0x00
		value = 1234
		# Initiation
		message_recv = bus2.recv()
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x40, index, subindex, 0x00000000))
		
		d = struct.pack("<BHBL", 0x4F, index, subindex, value)
		message_send = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message_send)
		time.sleep(0.001)
		
		message_recv = bus2.recv()
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, index, subindex, 0x06070010))
		
		#### Test step: Upload, expedited transfer, abort
		index = 0x5678
		subindex = 0x00
		value = 1234
		# Initiation
		message_recv = bus2.recv()
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x40, index, subindex, 0x00000000))
		
		d = struct.pack("<BHBL", 0x80, index, subindex, 0x05040000)
		message_send = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message_send)
		time.sleep(0.001)
		
		#### Test step: Upload, expedited transfer, wrong index in initiate response
		index = 0x5678
		subindex = 0x00
		value = 1234
		# Initiation
		message_recv = bus2.recv()
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x40, index, subindex, 0x00000000))
		
		d = struct.pack("<BHBL", 0x42, index ^ 0xFF, subindex, value)
		message_send = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message_send)
		time.sleep(0.001)
		
		message_recv = bus2.recv()
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, index ^ 0xFF, subindex, 0x08000000))

		#### Test step: Upload, expedited transfer, timeout
		index = 0x5678
		subindex = 0x00
		value = 1234
		# Initiation
		message_recv = bus2.recv()
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x40, index, subindex, 0x00000000))
		
		time.sleep(2)
		
		message_recv = bus2.recv()
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, index, subindex, 0x05040000))
		
		#### Test step: Upload, expedited transfer
		index = 0x5678
		subindex = 0x00
		value = 1234
		# Initiation
		message_recv = bus2.recv()
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x40, index, subindex, 0x00000000))
		
		d = struct.pack("<BHBL", 0x42, index, subindex, value)
		message_send = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message_send)
		time.sleep(0.001)
		
		#### Test step: Upload, segmented transfer, size not indicated
		index = 0x1234
		subindex = 0x0B
		value = "123456"
		# Initiation
		message_recv = bus2.recv()
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x40, index, subindex, 0x00000000))
		
		d = struct.pack("<BHBL", 0x40, index, subindex, len(value) * 2)
		message_send = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message_send)
		time.sleep(0.001)
		
		message_recv = bus2.recv()
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, index, subindex, 0x05040001))
		
		#### Test step: Upload, segmented transfer, toggle bit error
		index = 0x1234
		subindex = 0x0B
		value = "123456"
		# Initiation
		message_recv = bus2.recv()
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x40, index, subindex, 0x00000000))
		
		d = struct.pack("<BHBL", 0x41, index, subindex, len(value) * 2)
		message_send = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message_send)
		time.sleep(0.001)
		
		# First segment
		message_recv = bus2.recv()
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.data, struct.pack("<B7s", 0x60, b"\x00\x00\x00\x00\x00\x00\x00"))
		
		d = struct.pack("<B7s", 0x10, b"\x31\x00\x32\x00\x33\x00\x34")
		message_send = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message_send)
		time.sleep(0.001)
		
		message_recv = bus2.recv()
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, index, subindex, 0x05030000))
		
		#### Test step: Upload, segmented transfer, size does not match indicated size
		index = 0x1234
		subindex = 0x0B
		value = "123456"
		# Initiation
		message_recv = bus2.recv()
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x40, index, subindex, 0x00000000))
		
		d = struct.pack("<BHBL", 0x41, index, subindex, len(value))
		message_send = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message_send)
		time.sleep(0.001)
		
		# First segment
		message_recv = bus2.recv()
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.data, struct.pack("<B7s", 0x60, b"\x00\x00\x00\x00\x00\x00\x00"))
		
		d = struct.pack("<B7s", 0x00, b"\x31\x00\x32\x00\x33\x00\x34")
		message_send = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message_send)
		time.sleep(0.001)
		
		# Second and last segment
		message_recv = bus2.recv()
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.data, struct.pack("<B7s", 0x70, b"\x00\x00\x00\x00\x00\x00\x00"))
		
		d = struct.pack("<B7s", 0x15, b"\x00\x35\x00\x36\x00\x00\x00")
		message_send = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message_send)
		time.sleep(0.001)
		
		message_recv = bus2.recv()
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x80, index, subindex, 0x06070010))
		
		#### Test step: Upload, segmented transfer
		index = 0x1234
		subindex = 0x0B
		value = "123456"
		# Initiation
		message_recv = bus2.recv()
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x40, index, subindex, 0x00000000))
		
		d = struct.pack("<BHBL", 0x41, index, subindex, len(value) * 2)
		message_send = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message_send)
		time.sleep(0.001)
		
		# First segment
		message_recv = bus2.recv()
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.data, struct.pack("<B7s", 0x60, b"\x00\x00\x00\x00\x00\x00\x00"))
		
		d = struct.pack("<B7s", 0x00, b"\x31\x00\x32\x00\x33\x00\x34")
		message_send = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message_send)
		time.sleep(0.001)
		
		# Second and last segment
		message_recv = bus2.recv()
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.data, struct.pack("<B7s", 0x70, b"\x00\x00\x00\x00\x00\x00\x00"))
		
		d = struct.pack("<B7s", 0x15, b"\x00\x35\x00\x36\x00\x00\x00")
		message_send = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message_send)
		time.sleep(0.001)
		
		self.assertTrue(vehicle.is_alive())	
		vehicle.stop()
		vehicle.join()
		
		bus1.shutdown()
		bus2.shutdown()


if __name__ == "__main__":
	unittest.main()
