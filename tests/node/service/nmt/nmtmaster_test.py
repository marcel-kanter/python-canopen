import unittest
import time
import struct
import can
import canopen.node.service


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
		network.append(node)
		
		self.assertEqual(node.nmt.state, 0x00)
		
		#### Test step: Remote message -> Drop message
		message = can.Message(arbitration_id = 0x70A, is_extended_id = False, is_remote_frame = True, dlc = 1)
		bus2.send(message)
		time.sleep(0.001)
		
		self.assertEqual(node.nmt.state, 0x00)
		
		#### Test step: Missing data -> Drop message
		message = can.Message(arbitration_id = 0x70A, is_extended_id = False, data = b"")
		bus2.send(message)
		time.sleep(0.001)
		
		self.assertEqual(node.nmt.state, 0x00)
		
		#### Test step: Too much data -> Drop message
		message = can.Message(arbitration_id = 0x70A, is_extended_id = False, data = b"\x05\x05")
		bus2.send(message)
		time.sleep(0.001)
		
		self.assertEqual(node.nmt.state, 0x00)
		
		#### Test step: Remote message -> Drop message
		message = can.Message(arbitration_id = 0x70A, is_extended_id = False, is_remote_frame = True, dlc = 1)
		bus2.send(message)
		time.sleep(0.001)
		
		self.assertEqual(node.nmt.state, 0x00)
		
		#### Test step: NMT state with toggle bit
		message = can.Message(arbitration_id = 0x70A, is_extended_id = False, data = b"\x85")
		bus2.send(message)
		time.sleep(0.001)
		
		self.assertEqual(node.nmt.state, 0x05)
		
		#### Test step: NMT state without toggle bit
		message = can.Message(arbitration_id = 0x70A, is_extended_id = False, data = b"\x04")
		bus2.send(message)
		time.sleep(0.001)
		
		self.assertEqual(node.nmt.state, 0x04)
		
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
		network.append(node)
		
		#### Test step: Unknown state value -> ValueError
		with self.assertRaises(ValueError):
			node.nmt.state = 0xFF
		
		#### Test step: Reset application
		node.nmt.state = 0x00
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x00)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BB", 0x81, 0x0A))
		
		#### Test step: Enter preoperational
		node.nmt.state = 0x7F
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x00)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BB", 0x80, 0x0A))
		
		#### Test step: Operational
		node.nmt.state = 0x05
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x00)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BB", 0x01, 0x0A))
		
		#### Test step: Stopped
		node.nmt.state = 0x04
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x00)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BB", 0x02, 0x0A))
		
		network.detach()
		bus1.shutdown()
		bus2.shutdown()


if __name__ == "__main__":
	unittest.main()
