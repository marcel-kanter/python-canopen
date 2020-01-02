import unittest
from unittest.mock import Mock
import threading
import sys
import time
import can
import canopen.node.service
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
			network = canopen.Network()
			dictionary = canopen.ObjectDictionary()
			node = canopen.Node("a", 1, dictionary)
			examinee = canopen.node.service.PDOConsumer()
			
			network.attach(self._bus)
			node.attach(network)
			examinee.attach(node)
			
			self._barrier.wait(1)
			
			assert(examinee.wait(1))
			
			self._barrier.wait(1)
			
			assert(examinee.wait())
			
			examinee.detach()
			node.detach()
			network.detach()
		except AssertionError:
			self._testcase.result.addFailure(self._testcase, sys.exc_info())
		except:
			self._testcase.result.addError(self._testcase, sys.exc_info())

class PDOConsumerTest(unittest.TestCase):
	def test_init(self):
		test_data = [-1, 241, 253, 256]
		for value in test_data:
			with self.assertRaises(ValueError):
				PDOConsumer(value)
		
		examinee = PDOConsumer()
		
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
		examinee = PDOConsumer()
		
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
					examinee.attach(node1, value, 0)
				with self.assertRaises(ValueError):
					examinee.attach(node1, 0, value)
		
		examinee.attach(node1)
		self.assertEqual(examinee.node, node1)
		
		with self.assertRaises(ValueError):
			examinee.attach(node1)
		
		examinee.attach(node2, (1 << 29) | (0x200 + node2.id), (1 << 29) | 0x80)
		self.assertEqual(examinee.node, node2)
		
		examinee.detach()
		self.assertEqual(examinee.node, None)
		
		del network[node1.name]
		del network[node2.name]
	
	def test_pdo(self):
		bus1 = can.Bus(interface = "virtual", channel = 0)
		bus2 = can.Bus(interface = "virtual", channel = 0)
		network = canopen.Network()
		dictionary = canopen.ObjectDictionary()
		node = canopen.Node("a", 1, dictionary)
		examinee = PDOConsumer()
		
		cb1 = Mock()
		examinee.add_callback("pdo", cb1)
		
		network.attach(bus1)
		node.attach(network)
		
		examinee.attach(node)
		
		#### Test step: PDO message
		test_data = [b"\x11\x22\x33\x44\x55\x66\x77\x88", b"\x00", b""]
		for data in test_data:
			with self.subTest("PDO message", data = data):
				cb1.reset_mock()
				message = can.Message(arbitration_id = 0x201, is_extended_id = False, data = data)
				bus2.send(message)
				time.sleep(0.001)
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
		network = canopen.Network()
		dictionary = canopen.ObjectDictionary()
		node = canopen.Node("a", 1, dictionary)
		examinee = PDOConsumer()
		
		cb1 = Mock()
		examinee.add_callback("sync", cb1)
		
		network.attach(bus1)
		node.attach(network)
		examinee.attach(node)
		
		#### Test step: Sync message
		test_data = [(None, None), (b"", None), (b"\x01", 1)]
		for data, counter in test_data:
			with self.subTest("sync message", data = data):
				cb1.reset_mock()
				message = can.Message(arbitration_id = 0x80, is_extended_id = False, data = data)
				bus2.send(message)
				time.sleep(0.001)
				cb1.assert_called_with("sync", examinee, counter)
		
		#### Test step: sync message, ignore remote frame
		cb1.reset_mock()
		message = can.Message(arbitration_id = 0x80, is_extended_id = True, data = b"\x01")
		bus2.send(message)
		time.sleep(0.001)
		cb1.assert_not_called()
		
		#### Test step: sync message, ignore remote frame
		cb1.reset_mock()
		message = can.Message(arbitration_id = 0x80, is_extended_id = False, is_remote_frame = True, dlc = 1)
		bus2.send(message)
		time.sleep(0.001)
		cb1.assert_not_called()
		
		examinee.detach()
		node.detach()
		network.detach()
		bus1.shutdown()
		bus2.shutdown()
	
	def test_wait(self):
		bus1 = can.Bus(interface = "virtual", channel = 0)
		bus2 = can.Bus(interface = "virtual", channel = 0)
		
		vehicle = Vehicle_Wait(self, bus1)
		vehicle.start()

		vehicle.sync(1)
		
		time.sleep(0.1)
		
		message = can.Message(arbitration_id = 0x201, is_extended_id = False, data = b"\x11\x22\x33\x44\x55\x66\x77\x88")
		bus2.send(message)
		time.sleep(0.001)
		
		vehicle.sync(1)
		
		time.sleep(0.1)
		
		message = can.Message(arbitration_id = 0x201, is_extended_id = False, data = b"\x11\x22\x33\x44\x55\x66\x77\x88")
		bus2.send(message)
		time.sleep(0.001)
		
		vehicle.join(1)
		
		bus1.shutdown()
		bus2.shutdown()


if __name__ == "__main__":
	unittest.main()