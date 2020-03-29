import unittest
from unittest.mock import Mock
import threading
import sys
import time
import can

from canopen import Node, Network
from canopen.objectdictionary import ObjectDictionary
from canopen.node.service.pdo import PDOConsumer


class Vehicle_Wait(threading.Thread):
	def __init__(self, testcase, bus):
		threading.Thread.__init__(self, daemon = True)
		self._testcase = testcase
		self._bus = bus
		self._barrier = threading.Barrier(2)
	
	def sync(self, timeout = None):
		self._barrier.wait(timeout)
	
	def run(self):
		try:
			self.sync(1)
			time.sleep(0.1)
			message = can.Message(arbitration_id = 0x201, is_extended_id = False, data = b"\x11\x22\x33\x44\x55\x66\x77\x88")
			self._bus.send(message)
		
			self.sync(1)
			time.sleep(0.1)
			message = can.Message(arbitration_id = 0x201, is_extended_id = False, data = b"\x22\x22\x33\x44\x55\x66\x77\x88")
			self._bus.send(message)
			
			self.sync(1)
			time.sleep(0.1)
			message = can.Message(arbitration_id = 0x201, is_extended_id = False, data = b"\x33\x22\x33\x44\x55\x66\x77\x88")
			self._bus.send(message)
			
			self.sync(1)
			
		except AssertionError:
			self._testcase.result.addFailure(self._testcase, sys.exc_info())
		except:
			self._testcase.result.addError(self._testcase, sys.exc_info())

class PDOConsumerTest(unittest.TestCase):
	def test_init(self):
		dictionary = ObjectDictionary()
		node = Node("n", 1, dictionary)
		
		test_data = [-1, 241, 253, 256]
		for value in test_data:
			with self.assertRaises(ValueError):
				PDOConsumer(node, value)
		
		examinee = PDOConsumer(node)
		
		self.assertEqual(examinee.node, node)
		
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
		dictionary = ObjectDictionary()
		node = Node("n", 1, dictionary)
		examinee = PDOConsumer(node)
		network = Network()
		
		node.attach(network)
		
		with self.assertRaises(RuntimeError):
			examinee.detach()
		
		test_data = [-1, 0x100000000]
		for value in test_data:
			with self.subTest(value = value):
				with self.assertRaises(ValueError):
					examinee.attach(value, 0)
				with self.assertRaises(ValueError):
					examinee.attach(0, value)
		
		examinee.attach()
		self.assertTrue(examinee.is_attached())
		
		examinee.attach((1 << 29) | (0x200 + node.id), (1 << 29) | 0x80)
		self.assertTrue(examinee.is_attached())
		
		examinee.detach()
		self.assertFalse(examinee.is_attached())
		
		node.detach()
	
	def test_pdo(self):
		bus1 = can.Bus(interface = "virtual", channel = 0)
		bus2 = can.Bus(interface = "virtual", channel = 0)
		dictionary = ObjectDictionary()
		node = Node("a", 1, dictionary)
		examinee = PDOConsumer(node)
		network = Network()
		
		cb1 = Mock()
		examinee.add_callback("pdo", cb1)
		
		network.attach(bus1)
		node.attach(network)
		examinee.attach()
		
		#### Test step: PDO message
		test_data = [b"\x11\x22\x33\x44\x55\x66\x77\x88", b"\x00", b""]
		for data in test_data:
			with self.subTest("PDO message", data = data):
				cb1.reset_mock()
				message = can.Message(arbitration_id = 0x201, is_extended_id = False, data = data)
				bus2.send(message)
				time.sleep(0.01)
				cb1.assert_called_with("pdo", examinee)
				self.assertEqual(examinee.data, data)
		
		#### Test step: Enable/Disable Service
		cb1.reset_mock()
		examinee.disable()
		data = b"\x11\x22\x33"
		message = can.Message(arbitration_id = 0x201, is_extended_id = False, data = data)
		bus2.send(message)
		time.sleep(0.01)
		cb1.assert_not_called()
		examinee.enable()
		
		cb1.reset_mock()
		data = b"\x11\x22\x33\x44\x55"
		message = can.Message(arbitration_id = 0x201, is_extended_id = False, data = data)
		bus2.send(message)
		time.sleep(0.01)
		cb1.assert_called_with("pdo", examinee)
		self.assertEqual(examinee.data, data)
		
		#### Test step: PDO message, ignore differend extended frame type
		cb1.reset_mock()
		message = can.Message(arbitration_id = 0x201, is_extended_id = True, data = b"\x11\x22\x33\x44\x55\x66\x77\x88")
		bus2.send(message)
		time.sleep(0.01)
		cb1.assert_not_called()
		
		#### Test step: PDO message, ignore remote frame
		cb1.reset_mock()
		message = can.Message(arbitration_id = 0x201, is_extended_id = False, is_remote_frame = True, dlc = 1)
		bus2.send(message)
		time.sleep(0.01)
		cb1.assert_not_called()
		
		examinee.detach()
		node.detach()
		network.detach()
		bus1.shutdown()
		bus2.shutdown()
	
	def test_sync(self):
		bus1 = can.Bus(interface = "virtual", channel = 0)
		bus2 = can.Bus(interface = "virtual", channel = 0)
		dictionary = ObjectDictionary()
		node = Node("a", 1, dictionary)
		examinee = PDOConsumer(node)
		network = Network()
		
		cb1 = Mock()
		examinee.add_callback("sync", cb1)
		
		network.attach(bus1)
		node.attach(network)
		examinee.attach()
		
		#### Test step: Sync message
		test_data = [(None, None), (b"", None), (b"\x01", 1)]
		for data, counter in test_data:
			with self.subTest("sync message", data = data):
				cb1.reset_mock()
				message = can.Message(arbitration_id = 0x80, is_extended_id = False, data = data)
				bus2.send(message)
				time.sleep(0.01)
				cb1.assert_called_with("sync", examinee, counter)
		
		#### Test step: Sync message, enable/disbale service
		cb1.reset_mock()
		examinee.disable()
		message = can.Message(arbitration_id = 0x80, is_extended_id = False, data = None)
		bus2.send(message)
		time.sleep(0.01)
		cb1.assert_not_called()
		examinee.enable()
		
		cb1.reset_mock()
		message = can.Message(arbitration_id = 0x80, is_extended_id = False, data = None)
		bus2.send(message)
		time.sleep(0.01)
		cb1.assert_called_with("sync", examinee, None)
		
		#### Test step: sync message, ignore remote frame
		cb1.reset_mock()
		message = can.Message(arbitration_id = 0x80, is_extended_id = True, data = b"\x01")
		bus2.send(message)
		time.sleep(0.01)
		cb1.assert_not_called()
		
		#### Test step: sync message, ignore remote frame
		cb1.reset_mock()
		message = can.Message(arbitration_id = 0x80, is_extended_id = False, is_remote_frame = True, dlc = 1)
		bus2.send(message)
		time.sleep(0.01)
		cb1.assert_not_called()
		
		examinee.detach()
		node.detach()
		network.detach()
		bus1.shutdown()
		bus2.shutdown()
	
	def test_wait_for_pdo(self):
		bus1 = can.ThreadSafeBus(interface = "virtual", channel = 0)
		bus2 = can.ThreadSafeBus(interface = "virtual", channel = 0)
		dictionary = ObjectDictionary()
		node = Node("a", 1, dictionary)
		examinee = PDOConsumer(node)
		network = Network()
		
		network.attach(bus1)
		node.attach(network)
		examinee.attach()
		
		vehicle = Vehicle_Wait(self, bus2)
		vehicle.start()
		
		vehicle.sync(1)
		self.assertTrue(examinee.wait_for_pdo(0.5))
		
		vehicle.sync(1)
		self.assertTrue(examinee.wait_for_pdo())
		
		examinee.disable()
		vehicle.sync(1)
		self.assertFalse(examinee.wait_for_pdo(0.5))
		examinee.enable()
		
		vehicle.sync(1)
		self.assertFalse(examinee.wait_for_pdo(0.5))
		
		vehicle.join(1)
		
		examinee.detach()
		node.detach()
		network.detach()
		bus1.shutdown()
		bus2.shutdown()


if __name__ == "__main__":
	unittest.main()
