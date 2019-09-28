import unittest
import time
import struct
import can
import canopen.node.service
import canopen.nmt.states


class NMTMasterTestCase(unittest.TestCase):
	def test_init(self):
		nmt = canopen.node.service.NMTMaster()
		self.assertEqual(nmt.state, 0x00)
	
	def test_attach_detach(self):
		network = canopen.Network()
		dictionary = canopen.ObjectDictionary()
		node1 = canopen.Node("a", 1, dictionary)
		node2 = canopen.Node("b", 2, dictionary)
		examinee = canopen.node.service.NMTMaster()
		
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
	
	def test_error_control(self):
		bus1 = can.Bus(interface = "virtual", channel = 0)
		bus2 = can.Bus(interface = "virtual", channel = 0)
		network = canopen.Network()
		dictionary = canopen.ObjectDictionary()
		node = canopen.RemoteNode("a", 0x0A, dictionary)
		
		network.attach(bus1)
		network.add(node)
		
		self.assertEqual(node.nmt.state, canopen.nmt.states.INITIALIZATION)
		
		#### Test step: Remote message -> Drop message
		message = can.Message(arbitration_id = 0x700 + node.id, is_extended_id = False, is_remote_frame = True, dlc = 1)
		bus2.send(message)
		time.sleep(0.001)
		
		self.assertEqual(node.nmt.state, canopen.nmt.states.INITIALIZATION)
		
		#### Test step: Missing data -> Drop message
		message = can.Message(arbitration_id = 0x700 + node.id, is_extended_id = False, data = b"")
		bus2.send(message)
		time.sleep(0.001)
		
		self.assertEqual(node.nmt.state, canopen.nmt.states.INITIALIZATION)
		
		#### Test step: Too much data -> Drop message
		message = can.Message(arbitration_id = 0x700 + node.id, is_extended_id = False, data = b"\x05\x05")
		bus2.send(message)
		time.sleep(0.001)
		
		self.assertEqual(node.nmt.state, canopen.nmt.states.INITIALIZATION)
		
		#### Test step: Remote message -> Drop message
		message = can.Message(arbitration_id = 0x700 + node.id, is_extended_id = False, is_remote_frame = True, dlc = 1)
		bus2.send(message)
		time.sleep(0.001)
		
		self.assertEqual(node.nmt.state, canopen.nmt.states.INITIALIZATION)
		
		#### Test step: NMT state with toggle bit
		message = can.Message(arbitration_id = 0x700 + node.id, is_extended_id = False, data = b"\x85")
		bus2.send(message)
		time.sleep(0.001)
		
		self.assertEqual(node.nmt.state, canopen.nmt.states.OPERATIONAL)
		
		#### Test step: NMT state without toggle bit
		message = can.Message(arbitration_id = 0x700 + node.id, is_extended_id = False, data = b"\x04")
		bus2.send(message)
		time.sleep(0.001)
		
		self.assertEqual(node.nmt.state, canopen.nmt.states.STOPPED)
		
		#### Test step: Send guarding request
		node.nmt.send_guard_request()
		
		message = bus2.recv(1)
		self.assertEqual(message.arbitration_id, 0x700 + node.id)
		self.assertEqual(message.is_extended_id, False)
		self.assertEqual(message.is_remote_frame, True)
		self.assertEqual(message.dlc, 1)
		
		network.detach()
		bus1.shutdown()
		bus2.shutdown()
	
	def test_node_control(self):
		bus1 = can.Bus(interface = "virtual", channel = 0)
		bus2 = can.Bus(interface = "virtual", channel = 0)
		network = canopen.Network()
		dictionary = canopen.ObjectDictionary()
		node = canopen.RemoteNode("a", 0x0A, dictionary)
		
		network.attach(bus1)
		network.add(node)
		
		#### Test step: Unknown state value -> ValueError
		with self.assertRaises(ValueError):
			node.nmt.state = 0xFF
		
		#### Test step: Reset application
		node.nmt.state = canopen.nmt.states.INITIALIZATION
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x00)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BB", 0x81, 0x0A))
		
		#### Test step: Enter preoperational
		node.nmt.state = canopen.nmt.states.PRE_OPERATIONAL
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x00)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BB", 0x80, 0x0A))
		
		#### Test step: Operational
		node.nmt.state = canopen.nmt.states.OPERATIONAL
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x00)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BB", 0x01, 0x0A))
		
		#### Test step: Stopped
		node.nmt.state = canopen.nmt.states.STOPPED
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x00)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BB", 0x02, 0x0A))
		
		network.detach()
		bus1.shutdown()
		bus2.shutdown()
	
	def test_heartbeat(self):
		bus1 = can.Bus(interface = "virtual", channel = 0)
		bus2 = can.Bus(interface = "virtual", channel = 0)
		network = canopen.Network()
		dictionary = canopen.ObjectDictionary()
		node = canopen.RemoteNode("a", 0x0A, dictionary)
		
		network.attach(bus1)
		network.add(node)
		
		test_data = [-1.0, 0.0]
		for value in test_data:
			with self.subTest(value):
				with self.assertRaises(ValueError):
					node.nmt.start_heartbeat(value)
		
		node.nmt.start_heartbeat(0.2)
		
		del network[node.id]
		network.detach()
		bus1.shutdown()
		bus2.shutdown()
	
	def test_guarding(self):
		bus1 = can.Bus(interface = "virtual", channel = 0)
		bus2 = can.Bus(interface = "virtual", channel = 0)
		network = canopen.Network()
		dictionary = canopen.ObjectDictionary()
		node = canopen.RemoteNode("a", 0x0A, dictionary)
		
		network.attach(bus1)
		network.add(node)
		
		test_data = [-1.0, 0.0]
		for value in test_data:
			with self.subTest(value):
				with self.assertRaises(ValueError):
					node.nmt.start_guarding(value)
		
		node.nmt.start_guarding(0.2)
		time.sleep(0.05)
		
		message = bus2.recv(1)
		self.assertEqual(message.arbitration_id, 0x700 + node.id)
		self.assertEqual(message.is_remote_frame, True)
		self.assertEqual(message.dlc, 1)
		
		time.sleep(0.2)
		
		message = bus2.recv(1)
		self.assertEqual(message.arbitration_id, 0x700 + node.id)
		self.assertEqual(message.is_remote_frame, True)
		self.assertEqual(message.dlc, 1)
		
		node.nmt.stop()
		
		time.sleep(0.2)
		
		message = bus2.recv(0.01)
		self.assertEqual(message, None)
		
		del network[node.id]
		network.detach()
		bus1.shutdown()
		bus2.shutdown()


if __name__ == "__main__":
	unittest.main()
