import unittest
from unittest.mock import Mock
import canopen
import can


class NetworkTestCase(unittest.TestCase):
	def test_init(self):
		network = canopen.Network()
		bus = can.Bus(interface = "virtual", channel = 0)
		
		network.disconnect()
		
		network.connect(bus)
		
		network.connect(bus)
		
		network.disconnect()
		
		bus.shutdown()
	
	def test_message(self):
		network = canopen.Network()
		message = can.Message(arbitration_id = 0x100, data = [])
		
		network.on_message(message)


class MessageListenerTestCase(unittest.TestCase):
	def test_init(self):
		x = object()
		with self.assertRaises(TypeError):
			listener = canopen.network.MessageListener(x)
	
	def test_message(self):
		network = canopen.Network()
		listener = canopen.network.MessageListener(network)
		message = can.Message(arbitration_id = 0x100, data = [])
		
		network.on_message = Mock()
		
		listener.on_message_received(message)
		
		network.on_message.assert_called_once_with(message)


if __name__ == "__main__":
	unittest.main()
