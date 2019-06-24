import unittest
from unittest.mock import Mock
import time
import calendar
import struct
import can
import canopen.node.service.time


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
		examinee.add_callback(cb, "time")
		
		#### Test step: Message with time of CANopen epoch
		cb.reset_mock()
		d = struct.pack("<LH", 0, 0)
		message = can.Message(arbitration_id = 0x100, is_extended_id = False, data = d)
		bus2.send(message)
		time.sleep(0.001)
		cb.assert_called_with("time", node, calendar.timegm((1984, 1, 1, 0, 0, 0)))
		
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
		
		#### Test step: Message with some time - 60 days after CANopen epoch (1984 is a leap year)
		cb.reset_mock()
		d = struct.pack("<LH", 0, 60)
		message = can.Message(arbitration_id = 0x100, is_extended_id = False, data = d)
		bus2.send(message)
		time.sleep(0.001)
		cb.assert_called_with("time", node, calendar.timegm((1984, 3, 1, 0, 0, 0)))
		
		examinee.detach()
		node.detach()
		network.detach()
		bus1.shutdown()
		bus2.shutdown()
