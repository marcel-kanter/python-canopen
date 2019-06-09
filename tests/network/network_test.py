import unittest
from unittest.mock import Mock
import canopen.network
import can


class NetworkTestCase(unittest.TestCase):
	def test_init(self):
		canopen.Network()
	
	def test_attach_detach(self):
		network = canopen.Network()
		bus1 = can.Bus(interface = "virtual", channel = 0)
		bus2 = can.Bus(interface = "virtual", channel = 0)
		
		with self.assertRaises(RuntimeError):
			network.detach()
		
		with self.assertRaises(TypeError):
			network.attach(None)
		
		network.attach(bus1)
		
		with self.assertRaises(ValueError):
			network.attach(bus1)
		
		network.attach(bus2)
		
		network.detach()
		
		bus1.shutdown()
		bus2.shutdown()
	
	def test_message(self):
		network = canopen.Network()
		
		cb = Mock()
		network.subscribe(cb, 0x100)
		network.subscribe(self.__callback_raise, 0x100)
		
		message = can.Message(arbitration_id = 0x100, data = [])
		network.on_message(message)
		cb.assert_called_once()
		
		message = can.Message(arbitration_id = 0x200, data = [])
		network.on_message(message)
		cb.assert_called_once()
		
		network.unsubscribe(cb, 0x100)
		
		message = can.Message(arbitration_id = 0x100, data = [])
		network.on_message(message)
		cb.assert_called_once()
		
		network.unsubscribe(self.__callback_raise, 0x100)
	
	def test_subscribe(self):
		network = canopen.Network()
		
		cb = object()
		
		with self.assertRaises(TypeError):
			network.subscribe(cb, 0x100)
		
		with self.assertRaises(TypeError):
			network.unsubscribe(cb, 0x100)
		
		cb = Mock()
		
		network.subscribe(cb, 0x100)
		with self.assertRaises(KeyError):
			network.unsubscribe(cb, 0x200)
		network.unsubscribe(cb, 0x100)
	
	def test_collection(self):
		dictionary = canopen.ObjectDictionary()
		network = canopen.Network()
		
		# append
		x = canopen.Network()
		with self.assertRaises(TypeError):
			network.append(x)
		
		n1 = canopen.Node("n1", 10, dictionary)
		network.append(n1)
		self.assertEqual(len(network), 1)
		
		x = canopen.Node("n1", 20, dictionary)
		with self.assertRaises(ValueError):
			network.append(x)
		x = canopen.Node("n2", 10, dictionary)
		with self.assertRaises(ValueError):
			network.append(x)
		
		n2 = canopen.Node("n2", 20, dictionary)
		network.append(n2)
		self.assertEqual(len(network), 2)
		
		# contains
		self.assertFalse("xxx" in network)
		self.assertFalse(99 in network)
		self.assertTrue(n1.name in network)
		self.assertTrue(n1.id in network)
		self.assertTrue(n2.name in network)
		self.assertTrue(n2.id in network)
		
		# iter, getitem
		items = []
		for k in network:
			items.append(network[k])
		
		# delitem
		for x in items:
			del network[x.name]
		
		# len
		self.assertEqual(len(network), 0)
	
	def test_send(self):
		network = canopen.Network()
		bus1 = can.Bus(interface = "virtual", channel = 0)
		bus2 = can.Bus(interface = "virtual", channel = 0)
		
		#### Test step: Send on detached bus
		with self.assertRaises(RuntimeError):
			network.send(can.Message(arbitration_id = 0x00, dlc = 0))
		
		#### Test step: Send message and receive on other bus.
		network.attach(bus1)
		
		message_send = can.Message(arbitration_id = 0x100, is_extended_id = False, data = b"\x11\x22\x33\x44")
		network.send(message_send)
		
		message_recv = bus2.recv()
		self.assertEqual(message_recv.arbitration_id, message_send.arbitration_id)
		self.assertEqual(message_recv.is_extended_id, message_send.is_extended_id)
		self.assertEqual(message_recv.data, message_send.data)
		
		network.detach()
		
		bus1.shutdown()
		bus2.shutdown()
	
	def __callback_raise(self, message):
		raise Exception()


class MessageListenerTestCase(unittest.TestCase):
	def test_init(self):
		x = object()
		with self.assertRaises(TypeError):
			canopen.network.MessageListener(x)
	
	def test_message(self):
		network = canopen.Network()
		listener = canopen.network.MessageListener(network)
		message = can.Message(arbitration_id = 0x100, data = [])
		
		network.on_message = Mock()
		
		listener.on_message_received(message)
		
		network.on_message.assert_called_once_with(message)


if __name__ == "__main__":
	unittest.main()
