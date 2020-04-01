import unittest
from unittest.mock import Mock
import time
import struct
import can

from canopen import Node, Network
from canopen.objectdictionary import ObjectDictionary
from canopen.node.service.nmt import RemoteNMTSlave
from canopen.nmt.states import *


class RemoteNMTSlaveTestCase(unittest.TestCase):
	def test_init(self):
		dictionary = ObjectDictionary()
		node = Node("n", 1, dictionary)
		examinee = RemoteNMTSlave(node)
		
		self.assertEqual(examinee.node, node)
		
		self.assertEqual(examinee.state, INITIALIZATION)
	
	def test_attach_detach(self):
		dictionary = ObjectDictionary()
		node = Node("n", 1, dictionary)
		examinee = RemoteNMTSlave(node)
		network = Network()
		
		node.attach(network)
		
		with self.assertRaises(RuntimeError):
			examinee.detach()
				
		examinee.attach()
		self.assertTrue(examinee.is_attached())
		
		examinee.attach()
		self.assertTrue(examinee.is_attached())
		
		examinee.detach()
		self.assertFalse(examinee.is_attached())
		
		node.detach()
	
	def test_error_control(self):
		bus1 = can.Bus(interface = "virtual", channel = 0)
		bus2 = can.Bus(interface = "virtual", channel = 0)
		dictionary = ObjectDictionary()
		node = Node("a", 0x0A, dictionary)
		examinee = RemoteNMTSlave(node)
		network = Network()
		
		network.attach(bus1)
		node.attach(network)
		examinee.attach()
		
		self.assertEqual(examinee.state, INITIALIZATION)
		
		#### Test step: Remote message -> Drop message
		message = can.Message(arbitration_id = 0x700 + node.id, is_extended_id = False, is_remote_frame = True, dlc = 1)
		bus2.send(message)
		time.sleep(0.001)
		
		self.assertEqual(examinee.state, INITIALIZATION)
		
		#### Test step: Missing data -> Drop message
		message = can.Message(arbitration_id = 0x700 + node.id, is_extended_id = False, data = b"")
		bus2.send(message)
		time.sleep(0.001)
		
		self.assertEqual(examinee.state, INITIALIZATION)
		
		#### Test step: Too much data -> Drop message
		message = can.Message(arbitration_id = 0x700 + node.id, is_extended_id = False, data = b"\x05\x05")
		bus2.send(message)
		time.sleep(0.001)
		
		self.assertEqual(examinee.state, INITIALIZATION)
		
		#### Test step: Remote message -> Drop message
		message = can.Message(arbitration_id = 0x700 + node.id, is_extended_id = False, is_remote_frame = True, dlc = 1)
		bus2.send(message)
		time.sleep(0.001)
		
		self.assertEqual(examinee.state, INITIALIZATION)
		
		#### Test step: NMT state with toggle bit
		message = can.Message(arbitration_id = 0x700 + node.id, is_extended_id = False, data = b"\x85")
		bus2.send(message)
		time.sleep(0.001)
		
		self.assertEqual(examinee.state, OPERATIONAL)
		
		#### Test step: NMT state without toggle bit
		message = can.Message(arbitration_id = 0x700 + node.id, is_extended_id = False, data = b"\x04")
		bus2.send(message)
		time.sleep(0.001)
		
		self.assertEqual(examinee.state, STOPPED)
		
		#### Test step: Send guarding request
		examinee.send_guard_request()
		
		message = bus2.recv(1)
		self.assertEqual(message.arbitration_id, 0x700 + node.id)
		self.assertEqual(message.is_extended_id, False)
		self.assertEqual(message.is_remote_frame, True)
		self.assertEqual(message.dlc, 1)
		
		examinee.detach()
		node.detach()
		network.detach()
		bus1.shutdown()
		bus2.shutdown()
	
	def test_node_control(self):
		bus1 = can.Bus(interface = "virtual", channel = 0)
		bus2 = can.Bus(interface = "virtual", channel = 0)
		dictionary = ObjectDictionary()
		node = Node("a", 0x0A, dictionary)
		examinee = RemoteNMTSlave(node)
		network = Network()
		
		network.attach(bus1)
		node.attach(network)
		examinee.attach()
		
		#### Test step: Unknown state value -> ValueError
		with self.assertRaises(ValueError):
			examinee.state = 0xFF
		
		#### Test step: Reset application
		examinee.state = INITIALIZATION
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x00)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BB", 0x81, 0x0A))
		
		#### Test step: Enter preoperational
		examinee.state = PRE_OPERATIONAL
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x00)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BB", 0x80, 0x0A))
		
		#### Test step: Operational
		examinee.state = OPERATIONAL
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x00)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BB", 0x01, 0x0A))
		
		#### Test step: Stopped
		examinee.state = STOPPED
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x00)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BB", 0x02, 0x0A))
		
		#### Test step: Manual send command
		with self.assertRaises(ValueError):
			examinee.send_command(-1)
		
		with self.assertRaises(ValueError):
			examinee.send_command(256)
		
		examinee.send_command(0x81)
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x00)
		self.assertEqual(message_recv.is_extended_id, False)
		self.assertEqual(message_recv.data, struct.pack("<BB", 0x81, 0x0A))
		
		examinee.detach()
		node.detach()
		network.detach()
		bus1.shutdown()
		bus2.shutdown()
	
	def test_heartbeat(self):
		bus1 = can.Bus(interface = "virtual", channel = 0)
		bus2 = can.Bus(interface = "virtual", channel = 0)
		dictionary = ObjectDictionary()
		node = Node("a", 0x0A, dictionary)
		examinee = RemoteNMTSlave(node)
		network = Network()
		
		cb = Mock()
		
		examinee.add_callback("heartbeat", cb)
		
		network.attach(bus1)
		node.attach(network)
		examinee.attach()
		
		test_data = [-1.0, 0.0]
		for value in test_data:
			with self.subTest("heartbeat_time=" + str(value)):
				with self.assertRaises(ValueError):
					examinee.start_heartbeat(value)
		
		examinee.start_heartbeat(0.2)
		start_time = time.time()
		
		message = can.Message(arbitration_id = 0x700 + node.id, is_extended_id = False, is_remote_frame = False, data = b"\x05")
		bus2.send(message)
		
		time.sleep(0.05 + start_time - time.time())
		self.assertEqual(examinee.state, 0x05)
		time.sleep(0.15 + start_time - time.time())
		
		cb.assert_not_called()
		
		message = can.Message(arbitration_id = 0x700 + node.id, is_extended_id = False, is_remote_frame = False, data = b"\x7F")
		bus2.send(message)
		
		time.sleep(0.2 + start_time - time.time())
		self.assertEqual(examinee.state, 0x7F)
		
		time.sleep(0.3 + start_time - time.time())
		
		cb.assert_not_called()
		
		time.sleep(0.4 + start_time - time.time())
		
		cb.assert_called_with("heartbeat", examinee)
		
		examinee.stop()
		
		#### Test step: Calling the timer_callback from outside should not produce an error (it should only be called by the internal timer).
		cb.reset_mock()
		examinee.timer_callback()
		
		message = bus2.recv(0.1)
		self.assertEqual(message, None)
		
		cb.assert_not_called()
		
		examinee.detach()
		node.detach()
		network.detach()
		bus1.shutdown()
		bus2.shutdown()
	
	def test_guarding(self):
		bus1 = can.Bus(interface = "virtual", channel = 0)
		bus2 = can.Bus(interface = "virtual", channel = 0)
		dictionary = ObjectDictionary()
		node = Node("a", 0x0A, dictionary)
		examinee = RemoteNMTSlave(node)
		network = Network()
		
		cb = Mock()
		
		examinee.add_callback("guarding", cb)
		
		network.attach(bus1)
		node.attach(network)
		examinee.attach()
		
		test_data = [(-1, 1), (0, 1), (1, -1), (1, 0)]
		for guard_time, life_time_factor in test_data:
			with self.subTest("guard_time=" + str(guard_time) + ", life_time_factor=" + str(life_time_factor)):
				with self.assertRaises(ValueError):
					examinee.start_guarding(guard_time, life_time_factor)
		
		# Interval 0, t = 0
		examinee.start_guarding(0.1, 2)
		start_time = time.time()
		
		time.sleep(0.05 + start_time - time.time())
		
		message = bus2.recv(1)
		self.assertEqual(message.arbitration_id, 0x700 + node.id)
		self.assertEqual(message.is_remote_frame, True)
		self.assertEqual(message.dlc, 1)
		
		message = can.Message(arbitration_id = 0x700 + node.id, is_extended_id = False, is_remote_frame = False, data = b"\x05")
		bus2.send(message)
		
		time.sleep(0.15 + start_time - time.time())
		cb.assert_not_called()
		
		# Interval 1, t = 0.15
		
		message = bus2.recv(1)
		self.assertEqual(message.arbitration_id, 0x700 + node.id)
		self.assertEqual(message.is_remote_frame, True)
		self.assertEqual(message.dlc, 1)
		
		message = can.Message(arbitration_id = 0x700 + node.id, is_extended_id = False, is_remote_frame = False, data = b"\x85")
		bus2.send(message)
		
		time.sleep(0.25 + start_time - time.time())
		cb.assert_not_called()
		
		# Interval 2, t = 0.25, toggle bit not alternated
		
		message = bus2.recv(1)
		self.assertEqual(message.arbitration_id, 0x700 + node.id)
		self.assertEqual(message.is_remote_frame, True)
		self.assertEqual(message.dlc, 1)
		
		message = can.Message(arbitration_id = 0x700 + node.id, is_extended_id = False, is_remote_frame = False, data = b"\x85")
		bus2.send(message)
		
		time.sleep(0.35 + start_time - time.time())
		cb.assert_not_called()
		
		# Interval 3, t = 0.35, toggle bit not alternated
		
		message = bus2.recv(1)
		self.assertEqual(message.arbitration_id, 0x700 + node.id)
		self.assertEqual(message.is_remote_frame, True)
		self.assertEqual(message.dlc, 1)
		
		message = can.Message(arbitration_id = 0x700 + node.id, is_extended_id = False, is_remote_frame = False, data = b"\x85")
		bus2.send(message)
		
		time.sleep(0.45 + start_time - time.time())
		cb.assert_called_with("guarding", examinee)
		cb.reset_mock()
		
		# Interval 4, t = 0.45
		
		message = bus2.recv(1)
		self.assertEqual(message.arbitration_id, 0x700 + node.id)
		self.assertEqual(message.is_remote_frame, True)
		self.assertEqual(message.dlc, 1)
		
		message = can.Message(arbitration_id = 0x700 + node.id, is_extended_id = False, is_remote_frame = False, data = b"\x05")
		bus2.send(message)
		
		time.sleep(0.55 + start_time - time.time())
		cb.assert_not_called()
		
		# Interval 5, t = 0.55, without response
		
		message = bus2.recv(1)
		self.assertEqual(message.arbitration_id, 0x700 + node.id)
		self.assertEqual(message.is_remote_frame, True)
		self.assertEqual(message.dlc, 1)
		
		time.sleep(0.65 + start_time - time.time())
		cb.assert_not_called() # life time factor = 2 => the event occurs on second missed guarding request
		
		# Interval 6, t = 0.65, without response
		
		message = bus2.recv(1)
		self.assertEqual(message.arbitration_id, 0x700 + node.id)
		self.assertEqual(message.is_remote_frame, True)
		self.assertEqual(message.dlc, 1)
		
		time.sleep(0.75 + start_time - time.time())
		
		cb.assert_called_with("guarding", examinee)
		
		# Interval 7, t = 0.75, stop
		
		message = bus2.recv(1)
		self.assertEqual(message.arbitration_id, 0x700 + node.id)
		self.assertEqual(message.is_remote_frame, True)
		self.assertEqual(message.dlc, 1)
		
		examinee.stop()
		
		message = bus2.recv(0.2)
		self.assertEqual(message, None)
		
		#### Test step: Calling the timer_callback from outside should not produce an error (it should only be called by the internal timer).
		cb.reset_mock()
		examinee.timer_callback()
		
		message = bus2.recv(0.1)
		self.assertEqual(message, None)
		
		cb.assert_not_called()
		
		examinee.detach()
		node.detach()
		network.detach()
		bus1.shutdown()
		bus2.shutdown()


if __name__ == "__main__":
	unittest.main()
