import unittest
from unittest.mock import Mock
import time
import struct
import can
import canopen.node.service


class EMCYConsumerTestCase(unittest.TestCase):
	def test_init(self):
		canopen.node.service.EMCYConsumer()
	
	def test_attach_detach(self):
		dictionary = canopen.ObjectDictionary()
		network = canopen.Network()
		node1 = canopen.Node("a", 1, dictionary)
		node2 = canopen.Node("b", 2, dictionary)
		examinee = canopen.node.service.EMCYConsumer()
		
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
	
	def test_callback(self):
		consumer = canopen.node.service.EMCYConsumer()
		
		cb1 = Mock()
		cb2 = Mock()
		
		#### Test step: Callback is not callable
		with self.assertRaises(TypeError):
			consumer.add_callback("emcy", None)
		
		#### Test step: Event not known
		with self.assertRaises(ValueError):
			consumer.add_callback("xxx", cb1)
		
		#### Test step: Add callbacks, one which raises an exception
		consumer.add_callback("emcy", cb1)
		consumer.add_callback("emcy", self.__callback_raise)
		consumer.add_callback("emcy", self.__callback_emcy)
		consumer.add_callback("emcy", cb2)
		
		#### Test step: Try to notify an unknown event
		with self.assertRaises(ValueError):
			consumer.notify("xxx", consumer, 0x1000, 0x00, b"\x00\x00\x00\x00\x00")
		
		#### Test step: Notify a known event
		consumer.notify("emcy", consumer, 0x1000, 0x00, b"\x00\x00\x00\x00\x00")
		
		cb1.assert_called_once_with("emcy", consumer, 0x1000, 0x00, b"\x00\x00\x00\x00\x00")
		cb2.assert_called_once_with("emcy", consumer, 0x1000, 0x00, b"\x00\x00\x00\x00\x00")
		
		#### Test step: Remove callbacks
		with self.assertRaises(TypeError):
			consumer.remove_callback("emcy", None)
		
		with self.assertRaises(ValueError):
			consumer.remove_callback("xxx", cb1)
		
		consumer.remove_callback("emcy", cb1)
		consumer.remove_callback("emcy", cb2)
		consumer.remove_callback("emcy", self.__callback_raise)
		consumer.remove_callback("emcy", self.__callback_emcy)
	
	def test_on_emcy(self):
		bus1 = can.Bus(interface = "virtual", channel = 0)
		bus2 = can.Bus(interface = "virtual", channel = 0)
		network = canopen.Network()
		dictionary = canopen.ObjectDictionary()
		node = canopen.Node("a", 1, dictionary)
		consumer = canopen.node.service.EMCYConsumer()
		
		cb1 = Mock()
		
		network.attach(bus1)
		node.attach(network)
		consumer.attach(node)
		
		consumer.add_callback("emcy", cb1)
		
		#### Test step: EMCY write no error, or error reset
		with self.subTest("EMCY write no error, or error reset"):
			cb1.reset_mock()
			d = struct.pack("<HB5s", 0x0000, 0x00, b"\x00\x00\x00\x00\x00")
			message = can.Message(arbitration_id = 0x80 + node.id, is_extended_id = False, data = d)
			bus2.send(message)
			time.sleep(0.001)
			cb1.assert_called_once_with("emcy", consumer, 0x0000, 0x00, b"\x00\x00\x00\x00\x00")
		
		#### Test step: EMCY write with malformed message - too short message
		with self.subTest("EMCY write with malformed message - too short message"):
			cb1.reset_mock()
			d = struct.pack("<HB4s", 0x0000, 0x00, b"\x00\x00\x00\x00")
			message = can.Message(arbitration_id = 0x80 + node.id, is_extended_id = False, data = d)
			bus2.send(message)
			time.sleep(0.001)
			cb1.assert_not_called()
		
		consumer.detach()
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
