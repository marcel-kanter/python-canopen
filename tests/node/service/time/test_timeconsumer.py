import unittest
from unittest.mock import Mock
import threading
import sys
import time
import calendar
import struct
import can
import canopen.node.service.time


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
			self._barrier.wait(1)
			time.sleep(0.1)
			d = struct.pack("<LH", 0, 60)
			message = can.Message(arbitration_id = 0x100, is_extended_id = False, data = d)
			self._bus.send(message)
			
			self._barrier.wait(1)
			d = struct.pack("<LH", 0, 60)
			message = can.Message(arbitration_id = 0x100, is_extended_id = False, data = d)
			self._bus.send(message)
			
			self._barrier.wait(1)

		except AssertionError:
			self._testcase.result.addFailure(self._testcase, sys.exc_info())
		except:
			self._testcase.result.addError(self._testcase, sys.exc_info())


class TIMEConsumerTestCase(unittest.TestCase):
	def test_init(self):
		canopen.node.service.time.TIMEConsumer()
	
	def test_attach_detach(self):
		dictionary = canopen.ObjectDictionary()
		network = canopen.Network()
		node1 = canopen.Node("a", 1, dictionary)
		node2 = canopen.Node("b", 2, dictionary)
		examinee = canopen.node.service.time.TIMEConsumer()
		
		node1.attach(network)
		node2.attach(network)
		
		self.assertEqual(examinee.node, None)
		
		with self.assertRaises(RuntimeError):
			examinee.detach()
		
		with self.assertRaises(TypeError):
			examinee.attach(None, 0x100)
		
		test_data = [-1, 0x100000000]
		for value in test_data:
			with self.subTest(value = value):
				with self.assertRaises(ValueError):
					examinee.attach(node1, value)
		
		examinee.attach(node1, 0x100)
		self.assertEqual(examinee.node, node1)
		
		with self.assertRaises(ValueError):
			examinee.attach(node1, 0x100)
		
		examinee.attach(node2, (1 <<29) | 0x100)
		self.assertEqual(examinee.node, node2)
		
		examinee.detach()
		self.assertEqual(examinee.node, None)
		
		node1.detach()
		node2.detach()
	
	def test_on_sync(self):
		bus1 = can.Bus(interface = "virtual", channel = 0)
		bus2 = can.Bus(interface = "virtual", channel = 0)
		network = canopen.Network()
		dictionary = canopen.ObjectDictionary()
		node = canopen.Node("a", 1, dictionary)
		examinee = canopen.node.service.time.TIMEConsumer()
		
		network.attach(bus1)
		node.attach(network)
		examinee.attach(node)
		
		cb = Mock()
		examinee.add_callback("time", cb)
		
		#### Test step: Message with time of CANopen epoch
		cb.reset_mock()
		d = struct.pack("<LH", 0, 0)
		message = can.Message(arbitration_id = 0x100, is_extended_id = False, data = d)
		bus2.send(message)
		time.sleep(0.001)
		cb.assert_called_with("time", examinee, calendar.timegm((1984, 1, 1, 0, 0, 0)))
		
		#### Test step: Too short message
		cb.reset_mock()
		message = can.Message(arbitration_id = 0x100, is_extended_id = False, data = b"\x00")
		bus2.send(message)
		time.sleep(0.001)
		cb.assert_not_called()
		
		#### Test step: Ignore RTR
		cb.reset_mock()
		message = can.Message(arbitration_id = 0x100, is_extended_id = False, is_remote_frame = True, dlc = 6)
		bus2.send(message)
		time.sleep(0.001)
		cb.assert_not_called()
		
		#### Test step: Message with some time - 60 days after CANopen epoch (1984 is a leap year) but extended frame bit differs to cob_id
		cb.reset_mock()
		d = struct.pack("<LH", 0, 60)
		message = can.Message(arbitration_id = 0x100, is_extended_id = True, data = d)
		bus2.send(message)
		time.sleep(0.001)
		cb.assert_not_called()
		
		#### Test step: Message with some time - 60 days after CANopen epoch (1984 is a leap year)
		cb.reset_mock()
		d = struct.pack("<LH", 0, 60)
		message = can.Message(arbitration_id = 0x100, is_extended_id = False, data = d)
		bus2.send(message)
		time.sleep(0.001)
		cb.assert_called_with("time", examinee, calendar.timegm((1984, 3, 1, 0, 0, 0)))
		
		examinee.detach()
		node.detach()
		network.detach()
		bus1.shutdown()
		bus2.shutdown()
	
	def test_wait_for_time(self):
		bus1 = can.Bus(interface = "virtual", channel = 0)
		bus2 = can.Bus(interface = "virtual", channel = 0)
		
		vehicle = Vehicle_Wait(self, bus1)
		vehicle.start()
		
		network = canopen.Network()
		dictionary = canopen.ObjectDictionary()
		node = canopen.Node("a", 1, dictionary)
		examinee = canopen.node.service.TIMEConsumer()
		
		network.attach(bus2)
		node.attach(network)
		examinee.attach(node)
		
		vehicle.sync(1)
		self.assertTrue(examinee.wait_for_time(1))
		
		vehicle.sync(1)
		self.assertTrue(examinee.wait_for_time())
		
		vehicle.sync(1)
		self.assertFalse(examinee.wait_for_time(0.1))
		
		examinee.detach()
		node.detach()
		network.detach()
		
		vehicle.join(1)
		
		bus1.shutdown()
		bus2.shutdown()
