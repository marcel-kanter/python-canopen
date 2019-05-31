import unittest
import time
import can
import canopen.node.service


class SDOServerTestCase(unittest.TestCase):
	def test_init(self):
		canopen.node.service.SDOServer()
	
	def test_attach_detach(self):
		network = canopen.Network()
		dictionary = canopen.ObjectDictionary()
		node1 = canopen.Node("a", 1, dictionary)
		node2 = canopen.Node("b", 2, dictionary)
		sdoserver = canopen.node.service.SDOServer()
		
		node1.attach(network)
		node2.attach(network)
		
		with self.assertRaises(RuntimeError):
			sdoserver.detach()
		
		with self.assertRaises(TypeError):
			sdoserver.attach(None)
		
		sdoserver.attach(node1)
		
		with self.assertRaises(ValueError):
			sdoserver.attach(node1)
		
		sdoserver.attach(node2)
		
		sdoserver.detach()
		
		node1.detach()
		node2.detach()

	def test_request(self):
		bus = can.Bus(interface = "virtual", channel = 0, receive_own_messages = True)
		network = canopen.Network()
		dictionary = canopen.ObjectDictionary()
		node = canopen.Node("a", 1, dictionary)
		sdoserver = canopen.node.service.SDOServer()
		
		network.attach(bus)
		node.attach(network)
		sdoserver.attach(node)
		
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = b"\x00")
		bus.send(message)
		time.sleep(0.001)
		
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = b"\x00\x00\x00\x00\x00\x00\x00\x00")
		bus.send(message)
		time.sleep(0.001)
		
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = b"\x20\x00\x00\x00\x00\x00\x00\x00")
		bus.send(message)
		time.sleep(0.001)
		
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = b"\x40\x00\x00\x00\x00\x00\x00\x00")
		bus.send(message)
		time.sleep(0.001)
		
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = b"\x60\x00\x00\x00\x00\x00\x00\x00")
		bus.send(message)
		time.sleep(0.001)
		
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = b"\x80\x00\x00\x00\x00\x00\x00\x00")
		bus.send(message)
		time.sleep(0.001)
		
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = b"\xA0\x00\x00\x00\x00\x00\x00\x00")
		bus.send(message)
		time.sleep(0.001)
		
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = b"\xC0\x00\x00\x00\x00\x00\x00\x00")
		bus.send(message)
		time.sleep(0.001)
		
		message = can.Message(arbitration_id = 0x601, is_extended_id = False, data = b"\xE0\x00\x00\x00\x00\x00\x00\x00")
		bus.send(message)
		time.sleep(0.001)
		
		sdoserver.detach()
		node.detach()
		network.detach()
		bus.shutdown()


if __name__ == "__main__":
	unittest.main()
