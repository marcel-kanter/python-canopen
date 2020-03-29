import unittest
from unittest.mock import Mock
import threading
import sys
import time
import calendar
import struct
import can

from canopen import Node, Network
from canopen.objectdictionary import ObjectDictionary
from canopen.node.service.time import TIMEConsumer


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
			d = struct.pack("<LH", 0, 60)
			message = can.Message(arbitration_id = 0x100, is_extended_id = False, data = d)
			self._bus.send(message)
			
			self.sync(1)
			time.sleep(0.1)
			d = struct.pack("<LH", 1, 60)
			message = can.Message(arbitration_id = 0x100, is_extended_id = False, data = d)
			self._bus.send(message)
			
			self.sync(1)
			time.sleep(0.1)
			d = struct.pack("<LH", 2, 60)
			message = can.Message(arbitration_id = 0x100, is_extended_id = False, data = d)
			self._bus.send(message)
			
			self.sync(1)
		
		except AssertionError:
			self._testcase.result.addFailure(self._testcase, sys.exc_info())
		except:
			self._testcase.result.addError(self._testcase, sys.exc_info())


class TIMEConsumerTestCase(unittest.TestCase):
	def test_init(self):
		dictionary = ObjectDictionary()
		node = Node("n", 1, dictionary)
		examinee = TIMEConsumer(node)
		
		self.assertEqual(examinee.node, node)
	
	def test_attach_detach(self):
		dictionary = ObjectDictionary()
		node = Node("n", 1, dictionary)
		examinee = TIMEConsumer(node)
		network = Network()
		
		node.attach(network)
		
		with self.assertRaises(RuntimeError):
			examinee.detach()
		
		test_data = [-1, 0x100000000]
		for value in test_data:
			with self.subTest(value = value):
				with self.assertRaises(ValueError):
					examinee.attach(value)
		
		examinee.attach()
		self.assertTrue(examinee.is_attached())
		
		examinee.attach((1 << 29) | (0x100))
		self.assertTrue(examinee.is_attached())
		
		examinee.detach()
		self.assertFalse(examinee.is_attached())
		
		node.detach()
	
	def test_on_time(self):
		bus1 = can.Bus(interface = "virtual", channel = 0)
		bus2 = can.Bus(interface = "virtual", channel = 0)
		dictionary = ObjectDictionary()
		node = Node("a", 1, dictionary)
		examinee = TIMEConsumer(node)
		network = Network()
		
		network.attach(bus1)
		node.attach(network)
		examinee.attach()
		
		cb = Mock()
		examinee.add_callback("time", cb)
		
		#### Test step: Message with time of CANopen epoch
		cb.reset_mock()
		d = struct.pack("<LH", 0, 0)
		message = can.Message(arbitration_id = 0x100, is_extended_id = False, data = d)
		bus2.send(message)
		time.sleep(0.01)
		cb.assert_called_with("time", examinee, calendar.timegm((1984, 1, 1, 0, 0, 0)))
		
		#### Test step: Too short message
		cb.reset_mock()
		message = can.Message(arbitration_id = 0x100, is_extended_id = False, data = b"\x00")
		bus2.send(message)
		time.sleep(0.01)
		cb.assert_not_called()
		
		#### Test step: Ignore RTR
		cb.reset_mock()
		message = can.Message(arbitration_id = 0x100, is_extended_id = False, is_remote_frame = True, dlc = 6)
		bus2.send(message)
		time.sleep(0.01)
		cb.assert_not_called()
		
		#### Test step: Message with some time - 60 days after CANopen epoch (1984 is a leap year) but extended frame bit differs to cob_id
		cb.reset_mock()
		d = struct.pack("<LH", 0, 60)
		message = can.Message(arbitration_id = 0x100, is_extended_id = True, data = d)
		bus2.send(message)
		time.sleep(0.01)
		cb.assert_not_called()
		
		#### Test step: Message with some time, with disabled service
		cb.reset_mock()
		examinee.disable()
		d = struct.pack("<LH", 0, 60)
		message = can.Message(arbitration_id = 0x100, is_extended_id = False, data = d)
		bus2.send(message)
		time.sleep(0.01)
		cb.assert_not_called()
		examinee.enable()
		
		#### Test step: Message with some time - 60 days after CANopen epoch (1984 is a leap year)
		cb.reset_mock()
		d = struct.pack("<LH", 0, 60)
		message = can.Message(arbitration_id = 0x100, is_extended_id = False, data = d)
		bus2.send(message)
		time.sleep(0.01)
		cb.assert_called_with("time", examinee, calendar.timegm((1984, 3, 1, 0, 0, 0)))
		
		examinee.detach()
		node.detach()
		network.detach()
		bus1.shutdown()
		bus2.shutdown()
	
	def test_wait_for_time(self):
		bus1 = can.ThreadSafeBus(interface = "virtual", channel = 0)
		bus2 = can.ThreadSafeBus(interface = "virtual", channel = 0)
		dictionary = ObjectDictionary()
		node = Node("a", 1, dictionary)
		examinee = TIMEConsumer(node)
		network = Network()
		
		network.attach(bus1)
		node.attach(network)
		examinee.attach()
		
		vehicle = Vehicle_Wait(self, bus2)
		vehicle.start()
		
		vehicle.sync(1)
		self.assertTrue(examinee.wait_for_time(1))
		
		vehicle.sync(1)
		self.assertTrue(examinee.wait_for_time())
		
		examinee.disable()
		vehicle.sync(1)
		self.assertFalse(examinee.wait_for_time(0.4))
		examinee.enable()
		
		vehicle.sync(1)
		self.assertFalse(examinee.wait_for_time(0.4))
		
		vehicle.join(1)
		
		examinee.detach()
		node.detach()
		network.detach()
		bus1.shutdown()
		bus2.shutdown()


if __name__ == "__main__":
	unittest.main()
