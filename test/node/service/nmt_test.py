import unittest
import time
import can
import canopen.node.service


class NMTSlaveTestCase(unittest.TestCase):
	def test_init(self):
		nmt = canopen.node.service.NMTSlave()
		self.assertEqual(nmt.state, 0)
		
		with self.assertRaises(AttributeError):
			nmt.state = 0
	
	def test_attach_detach(self):
		network = canopen.Network()
		node1 = canopen.Node("a", 1)
		node2 = canopen.Node("b", 2)
		nmt = canopen.node.service.NMTSlave()
		
		node1.attach(network)
		node2.attach(network)
		
		with self.assertRaises(RuntimeError):
			nmt.detach()
		
		with self.assertRaises(TypeError):
			nmt.attach(None)
		
		nmt.attach(node1)
		
		with self.assertRaises(ValueError):
			nmt.attach(node1)
		
		nmt.attach(node2)
		
		nmt.detach()
		
		node1.detach()
		node2.detach()
	
	def test_node_control(self):
		bus = can.Bus(interface = "virtual", channel = 0, receive_own_messages = True)
		network = canopen.Network()
		node = canopen.LocalNode("a", 0x0A)
		
		network.attach(bus)
		network.append(node)
		
		self.assertEqual(node.nmt.state, 0x00)
		
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x00")
		bus.send(message)
		time.sleep(0.001)
		self.assertEqual(node.nmt.state, 0x00)
		
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x01\x10")
		bus.send(message)
		time.sleep(0.001)
		self.assertEqual(node.nmt.state, 0x00)
		
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x00\x0A")
		bus.send(message)
		time.sleep(0.001)
		self.assertEqual(node.nmt.state, 0x00)
		
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x00\x00")
		bus.send(message)
		time.sleep(0.001)
		self.assertEqual(node.nmt.state, 0x00)
		
		# Addressing by node id
		# Start (enter NMT operational)
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x01\x0A")
		bus.send(message)
		time.sleep(0.001)
		self.assertEqual(node.nmt.state, 0x05)
		
		# Enter NMT pre-operational
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x80\x0A")
		bus.send(message)
		time.sleep(0.001)
		self.assertEqual(node.nmt.state, 0x7F)
		
		# Enter NMT reset application
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x81\x0A")
		bus.send(message)
		time.sleep(0.001)
		self.assertEqual(node.nmt.state, 0x7F)
		
		# Stop (enter to NMT stopped)
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x02\x0A")
		bus.send(message)
		time.sleep(0.001)
		self.assertEqual(node.nmt.state, 0x04)
		
		# Enter NMT reset communication
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x82\x0A")
		bus.send(message)
		time.sleep(0.001)
		self.assertEqual(node.nmt.state, 0x7F)
		
		# Addressing by broadcast
		# Start (enter NMT operational)
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x01\x00")
		bus.send(message)
		time.sleep(0.001)
		self.assertEqual(node.nmt.state, 0x05)
		
		# Enter NMT pre-operational
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x80\x00")
		bus.send(message)
		time.sleep(0.001)
		self.assertEqual(node.nmt.state, 0x7F)
		
		# Enter NMT reset application
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x81\x00")
		bus.send(message)
		time.sleep(0.001)
		self.assertEqual(node.nmt.state, 0x7F)
		
		# Stop (enter to NMT stopped)
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x02\x00")
		bus.send(message)
		time.sleep(0.001)
		self.assertEqual(node.nmt.state, 0x04)
		
		# Enter NMT reset communication
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x82\x00")
		bus.send(message)
		time.sleep(0.001)
		self.assertEqual(node.nmt.state, 0x7F)
		
		network.detach()
		bus.shutdown()
	
	def test_error_control(self):
		bus1 = can.Bus(interface = "virtual", channel = 0)
		bus2 = can.Bus(interface = "virtual", channel = 0)
		network = canopen.Network()
		node = canopen.LocalNode("a", 0x0A)
		
		network.attach(bus1)
		network.append(node)
		
		message = can.Message(arbitration_id = 0x70A, is_extended_id = False, data = [])
		bus2.send(message)
		time.sleep(0.001)
		
		message = can.Message(arbitration_id = 0x70A, is_extended_id = False, is_remote_frame = True, dlc = 2)
		bus2.send(message)
		time.sleep(0.001)
		
		# Enter operational state
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x01\x0A")
		bus2.send(message)
		time.sleep(0.001)
		self.assertEqual(node.nmt.state, 0x05)
		
		message = can.Message(arbitration_id = 0x70A, is_extended_id = False, is_remote_frame = True, dlc = 1)
		bus2.send(message)
		time.sleep(0.001)
		
		message = bus2.recv()
		self.assertEqual(message.arbitration_id, 0x70A)
		self.assertEqual(message.is_remote_frame, False)
		self.assertEqual(message.data, b"\x05")
		
		message = can.Message(arbitration_id = 0x70A, is_extended_id = False, is_remote_frame = True, dlc = 1)
		bus2.send(message)
		time.sleep(0.001)
		
		message = bus2.recv()
		self.assertEqual(message.arbitration_id, 0x70A)
		self.assertEqual(message.is_remote_frame, False)
		self.assertEqual(message.data, b"\x85")
		
		message = can.Message(arbitration_id = 0x70A, is_extended_id = False, is_remote_frame = True, dlc = 1)
		bus2.send(message)
		time.sleep(0.001)
		
		message = bus2.recv()
		self.assertEqual(message.arbitration_id, 0x70A)
		self.assertEqual(message.is_remote_frame, False)
		self.assertEqual(message.data, b"\x05")
		
		# Reset communication - toggle bit should be reset to 0
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x82\x0A")
		bus2.send(message)
		time.sleep(0.001)
		self.assertEqual(node.nmt.state, 0x7F)
		
		message = can.Message(arbitration_id = 0x70A, is_extended_id = False, is_remote_frame = True, dlc = 1)
		bus2.send(message)
		time.sleep(0.001)
		
		message = bus2.recv()
		self.assertEqual(message.arbitration_id, 0x70A)
		self.assertEqual(message.is_remote_frame, False)
		self.assertEqual(message.data, b"\x7F")
		
		message = can.Message(arbitration_id = 0x70A, is_extended_id = False, is_remote_frame = True, dlc = 1)
		bus2.send(message)
		time.sleep(0.001)
		
		message = bus2.recv()
		self.assertEqual(message.arbitration_id, 0x70A)
		self.assertEqual(message.is_remote_frame, False)
		self.assertEqual(message.data, b"\xFF")
		
		message = can.Message(arbitration_id = 0x70A, is_extended_id = False, is_remote_frame = True, dlc = 1)
		bus2.send(message)
		time.sleep(0.001)
		
		message = bus2.recv()
		self.assertEqual(message.arbitration_id, 0x70A)
		self.assertEqual(message.is_remote_frame, False)
		self.assertEqual(message.data, b"\x7F")
		
		network.detach()
		bus1.shutdown()
		bus2.shutdown()


if __name__ == "__main__":
	unittest.main()
