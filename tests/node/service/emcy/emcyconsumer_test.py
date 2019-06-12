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
		consumer = canopen.node.service.EMCYConsumer()
		
		node1.attach(network)
		node2.attach(network)
		
		with self.assertRaises(RuntimeError):
			consumer.detach()
		
		with self.assertRaises(TypeError):
			consumer.attach(None)
		
		consumer.attach(node1)
		
		with self.assertRaises(ValueError):
			consumer.attach(node1)
		
		consumer.attach(node2)
		
		consumer.detach()
		
		node1.detach()
		node2.detach()
	
	def test_callback(self):
		consumer = canopen.node.service.EMCYConsumer()
		
		cb1 = Mock()
		cb2 = Mock()
		
		#### Test step: Callback is not callable
		with self.assertRaises(TypeError):
			consumer.add_callback(None, "emcy")
		
		#### Test step: Event not known
		with self.assertRaises(ValueError):
			consumer.add_callback(cb1, "xxx")
		
		#### Test step: Add callbacks, one which raises an exception
		consumer.add_callback(cb1, "emcy")
		consumer.add_callback(self.__callback_raise, "emcy")
		consumer.add_callback(self.__callback_emcy, "emcy")
		consumer.add_callback(cb2, "emcy")
		
		#### Test step: Try to notify an unknown event
		with self.assertRaises(ValueError):
			consumer.notify("xxx")
		
		#### Test step: Notify a known event
		consumer.notify("emcy", 0x1000, 0x00, b"\x00\x00\x00\x00\x00")
		
		cb1.assert_called_once()
		cb2.assert_called_once()
		
		#### Test step: Remove callbacks
		with self.assertRaises(TypeError):
			consumer.remove_callback(None, "emcy")
		
		with self.assertRaises(ValueError):
			consumer.remove_callback(cb1, "xxx")
		
		consumer.remove_callback(cb1, "emcy")
		consumer.remove_callback(cb2, "emcy")
		consumer.remove_callback(self.__callback_raise, "emcy")
		consumer.remove_callback(self.__callback_emcy, "emcy")
	
	def test_on_emcy(self):
		bus1 = can.Bus(interface = "virtual", channel = 0)
		bus2 = can.Bus(interface = "virtual", channel = 0)
		network = canopen.Network()
		dictionary = canopen.ObjectDictionary()
		node = canopen.Node("a", 1, dictionary)
		consumer = canopen.node.service.EMCYConsumer()
		
		network.attach(bus1)
		node.attach(network)
		consumer.attach(node)
		
		#### Test step: EMCY write "no error, or error reset"
		d = struct.pack("<HB5s", 0x0000, 0x00, b"\x00\x00\x00\x00\x00")
		message = can.Message(arbitration_id = 0x81, is_extended_id = False, data = d)
		bus2.send(message)
		time.sleep(0.001)
		
		consumer.detach()
		node.detach()
		network.detach()
		bus1.shutdown()
		bus2.shutdown()
	
	def __callback_emcy(self, event, node, error_code, error_register, data):
		print(error_code)
	
	def __callback_raise(self, event, node, *args):
		raise Exception()


if __name__ == "__main__":
	unittest.main()
