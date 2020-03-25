import unittest
from unittest.mock import Mock
import time
import struct
import can

from canopen import Node, Network
from canopen.objectdictionary import ObjectDictionary
from canopen.node.service.emcy import EMCYConsumer


class EMCYConsumerTestCase(unittest.TestCase):
	def test_init(self):
		dictionary = ObjectDictionary()
		node = Node("n", 1, dictionary)
		examinee = EMCYConsumer(node)
		
		self.assertEqual(examinee.node, node)
	
	def test_attach_detach(self):
		dictionary = ObjectDictionary()
		node = Node("n", 1, dictionary)
		examinee = EMCYConsumer(node)
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
		
		examinee.attach((1 << 29) | (0x80 + node.id))
		self.assertTrue(examinee.is_attached())
		
		examinee.detach()
		self.assertFalse(examinee.is_attached())
		
		node.detach()
	
	def test_callback(self):
		dictionary = ObjectDictionary()
		node = Node("n", 1, dictionary)
		examinee = EMCYConsumer(node)
		
		cb1 = Mock()
		cb2 = Mock()
		
		#### Test step: Add callbacks, one which raises an exception
		examinee.add_callback("emcy", cb1)
		examinee.add_callback("emcy", self.__callback_raise)
		examinee.add_callback("emcy", self.__callback_emcy)
		examinee.add_callback("emcy", cb2)
		
		#### Test step: Notify a known event
		examinee.notify("emcy", examinee, 0x1000, 0x00, b"\x00\x00\x00\x00\x00")
		
		cb1.assert_called_once_with("emcy", examinee, 0x1000, 0x00, b"\x00\x00\x00\x00\x00")
		cb2.assert_called_once_with("emcy", examinee, 0x1000, 0x00, b"\x00\x00\x00\x00\x00")
		
		#### Test step: Remove callbacks
		examinee.remove_callback("emcy", cb1)
		examinee.remove_callback("emcy", cb2)
		examinee.remove_callback("emcy", self.__callback_raise)
		examinee.remove_callback("emcy", self.__callback_emcy)
	
	def test_on_emcy(self):
		bus1 = can.Bus(interface = "virtual", channel = 0)
		bus2 = can.Bus(interface = "virtual", channel = 0)
		dictionary = ObjectDictionary()
		node = Node("a", 1, dictionary)
		examinee = EMCYConsumer(node)
		network = Network()
		
		network.attach(bus1)
		node.attach(network)
		examinee.attach()
		
		cb1 = Mock()
		examinee.add_callback("emcy", cb1)
		
		#### Test step: EMCY write no error, or error reset
		with self.subTest("EMCY write no error, or error reset"):
			cb1.reset_mock()
			d = struct.pack("<HB5s", 0x0000, 0x00, b"\x00\x00\x00\x00\x00")
			message = can.Message(arbitration_id = 0x80 + node.id, is_extended_id = False, data = d)
			bus2.send(message)
			time.sleep(0.001)
			cb1.assert_called_once_with("emcy", examinee, 0x0000, 0x00, b"\x00\x00\x00\x00\x00")
		
		#### Test step: EMCY write with differing extended frame bit
		with self.subTest("EMCY write with differing extended frame bit"):
			cb1.reset_mock()
			d = struct.pack("<HB4s", 0x0001, 0x00, b"\x00\x00\x00\x00\x00")
			message = can.Message(arbitration_id = 0x80 + node.id, is_extended_id = True, data = d)
			bus2.send(message)
			time.sleep(0.1)
			cb1.assert_not_called()
		
		#### Test step: EMCY write with malformed message - too short message
		with self.subTest("EMCY write with malformed message - too short message"):
			cb1.reset_mock()
			d = struct.pack("<HB4s", 0x0002, 0x00, b"\x00\x00\x00\x00")
			message = can.Message(arbitration_id = 0x80 + node.id, is_extended_id = False, data = d)
			bus2.send(message)
			time.sleep(0.1)
			cb1.assert_not_called()
		
		#### Test step: EMCY write with disabled service and re-enabled service
		with self.subTest("EMCY write with disabled service"):
			examinee.disable()
			cb1.reset_mock()
			d = struct.pack("<HB4s", 0x0003, 0x00, b"\x00\x00\x00\x00")
			message = can.Message(arbitration_id = 0x80 + node.id, is_extended_id = False, data = d)
			bus2.send(message)
			time.sleep(0.1)
			cb1.assert_not_called()
			
			examinee.enable()
			d = struct.pack("<HB5s", 0x0004, 0x00, b"\x00\x00\x00\x00\x00")
			message = can.Message(arbitration_id = 0x80 + node.id, is_extended_id = False, data = d)
			bus2.send(message)
			time.sleep(0.001)
			cb1.assert_called_once_with("emcy", examinee, 0x0004, 0x00, b"\x00\x00\x00\x00\x00")
		
		examinee.detach()
		node.detach()
		network.detach()
		bus1.shutdown()
		bus2.shutdown()
	
	def __callback_emcy(self, event, node, error_code, error_register, data):
		pass
	
	def __callback_raise(self, event, node, *args):
		raise Exception()


if __name__ == "__main__":
	unittest.main()
