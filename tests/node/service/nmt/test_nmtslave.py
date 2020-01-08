import unittest
from unittest.mock import Mock
import time
import can

from canopen import Node, Network
from canopen.objectdictionary import ObjectDictionary
from canopen.node.service.nmt import NMTSlave

from canopen.nmt.states import *


class NMTSlaveTestCase(unittest.TestCase):
	def test_init(self):
		dictionary = ObjectDictionary()
		node = Node("n", 1, dictionary)
		examinee = NMTSlave(node)
		
		self.assertEqual(examinee.node, node)
		
		self.assertEqual(examinee.state, INITIALIZATION)
		
		
		#### Test step: Check if unallowed values raise a ValueError
		with self.assertRaises(ValueError):
			examinee.state = 0x11
		
		#### Test step: Check if only transition to pre-operational state is allowed
		with self.assertRaises(ValueError):
			examinee.state = STOPPED
		
		with self.assertRaises(ValueError):
			examinee.state = OPERATIONAL
		
		examinee.state = PRE_OPERATIONAL
		self.assertEqual(examinee.state, PRE_OPERATIONAL)
		
		#### Test step: Check if all transitions are possible - the test cycles one time completely through all states in both directions
		test_data = [PRE_OPERATIONAL, OPERATIONAL, STOPPED, PRE_OPERATIONAL, STOPPED, OPERATIONAL, PRE_OPERATIONAL]
		for value in test_data:
			with self.subTest(value = value):
				examinee.state = value
				self.assertEqual(examinee.state, value)
	
	def test_attach_detach(self):
		dictionary = ObjectDictionary()
		node = Node("n", 1, dictionary)
		examinee = NMTSlave(node)
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
	
	def test_callback(self):
		dictionary = ObjectDictionary()
		node = Node("n", 1, dictionary)
		examinee = NMTSlave(node)
				
		m_start = Mock()
		m_stop = Mock()
		m_pre_operational = Mock()
		m_reset_application = Mock()
		m_reset_communication = Mock()
		m_raises = Mock(side_effect = self.__callback_raises)
		
		#### Test step: add callback
		examinee.add_callback("start", m_start)
		examinee.add_callback("stop", m_stop)
		examinee.add_callback("pre-operational", m_pre_operational)
		examinee.add_callback("reset-communication", m_reset_communication)
		examinee.add_callback("reset-application", m_reset_application)
		
		examinee.add_callback("start", m_raises)
		
		#### Test step: notify		
		examinee.notify("start", examinee)
		m_start.assert_called_once_with("start", examinee)
		m_stop.assert_not_called()
		m_pre_operational.assert_not_called()
		m_reset_application.assert_not_called()
		m_reset_communication.assert_not_called()
		m_raises.assert_called_once_with("start", examinee)
		
		examinee.notify("stop", examinee)
		m_start.assert_called_once()
		m_stop.assert_called_once_with("stop", examinee)
		m_pre_operational.assert_not_called()
		m_reset_application.assert_not_called()
		m_reset_communication.assert_not_called()
		m_raises.assert_called_once()
		
		examinee.notify("pre-operational", examinee)
		m_start.assert_called_once()
		m_stop.assert_called_once()
		m_pre_operational.assert_called_once_with("pre-operational", examinee)
		m_reset_application.assert_not_called()
		m_reset_communication.assert_not_called()
		m_raises.assert_called_once()
		
		examinee.notify("reset-application", examinee)
		m_start.assert_called_once()
		m_stop.assert_called_once()
		m_pre_operational.assert_called_once()
		m_reset_application.assert_called_once_with("reset-application", examinee)
		m_reset_communication.assert_not_called()
		m_raises.assert_called_once()
		
		examinee.notify("reset-communication", examinee)
		m_start.assert_called_once()
		m_stop.assert_called_once()
		m_pre_operational.assert_called_once()
		m_reset_application.assert_called_once()
		m_reset_communication.assert_called_once_with("reset-communication", examinee)
		m_raises.assert_called_once()
		
		#### Test step: Remove callbacks
		examinee.remove_callback("start", m_start)
		examinee.remove_callback("stop", m_stop)
		examinee.remove_callback("pre-operational", m_pre_operational)
		examinee.remove_callback("reset-application", m_reset_application)
		examinee.remove_callback("reset-communication", m_reset_communication)
		examinee.remove_callback("start", m_raises)
	
	def test_node_control(self):
		bus = can.Bus(interface = "virtual", channel = 0, receive_own_messages = True)
		dictionary = ObjectDictionary()
		node = Node("a", 0x0A, dictionary)
		examinee = NMTSlave(node)
		network = Network()
		
		network.attach(bus)
		node.attach(network)
		examinee.attach()
		
		examinee.add_callback("start", self.__callback_start)
		examinee.add_callback("stop", self.__callback_stop)
		examinee.add_callback("pre-operational", self.__callback_pre_operational)
		examinee.add_callback("reset-application", self.__callback_reset_application)
		examinee.add_callback("reset-communication", self.__callback_reset_communication)
		
		self.assertEqual(examinee.state, INITIALIZATION)
		
		#### Test step: Wrong data length
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x00")
		bus.send(message)
		time.sleep(0.001)
		self.assertEqual(examinee.state, INITIALIZATION)
		
		#### Test step: Wrong node id
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x01\x10")
		bus.send(message)
		time.sleep(0.001)
		self.assertEqual(examinee.state, INITIALIZATION)
		
		#### Test step: Unknown command with direct addressing
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x00\x0A")
		bus.send(message)
		time.sleep(0.001)
		self.assertEqual(examinee.state, INITIALIZATION)
		
		#### Test step: Unknwon command with broadcast
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x00\x00")
		bus.send(message)
		time.sleep(0.001)
		self.assertEqual(examinee.state, INITIALIZATION)
		
		#### Test step: Addressing with node id
		# Application somewhen finishes start-up and changes the node's nmt state to pre-operational
		examinee.state = PRE_OPERATIONAL
		
		# Start (enter NMT operational)
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x01\x0A")
		bus.send(message)
		time.sleep(0.001)
		self.assertEqual(examinee.state, OPERATIONAL)
		
		# Enter NMT pre-operational
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x80\x0A")
		bus.send(message)
		time.sleep(0.001)
		self.assertEqual(examinee.state, PRE_OPERATIONAL)
		
		# Enter NMT reset application
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x81\x0A")
		bus.send(message)
		time.sleep(0.001)
		self.assertEqual(examinee.state, PRE_OPERATIONAL)
		
		# Stop (enter to NMT stopped)
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x02\x0A")
		bus.send(message)
		time.sleep(0.001)
		self.assertEqual(examinee.state, STOPPED)
		
		# Enter NMT reset communication
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x82\x0A")
		bus.send(message)
		time.sleep(0.001)
		self.assertEqual(examinee.state, PRE_OPERATIONAL)
		
		#### Test step: Addressing with broadcast
		# Start (enter NMT operational)
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x01\x00")
		bus.send(message)
		time.sleep(0.001)
		self.assertEqual(examinee.state, OPERATIONAL)
		
		# Enter NMT pre-operational
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x80\x00")
		bus.send(message)
		time.sleep(0.001)
		self.assertEqual(examinee.state, PRE_OPERATIONAL)
		
		# Enter NMT reset application
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x81\x00")
		bus.send(message)
		time.sleep(0.001)
		self.assertEqual(examinee.state, PRE_OPERATIONAL)
		
		# Stop (enter to NMT stopped)
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x02\x00")
		bus.send(message)
		time.sleep(0.001)
		self.assertEqual(examinee.state, STOPPED)
		
		# Enter NMT reset communication
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x82\x00")
		bus.send(message)
		time.sleep(0.001)
		self.assertEqual(examinee.state, PRE_OPERATIONAL)
		
		examinee.detach()
		node.detach()
		network.detach()
		bus.shutdown()
	
	def test_error_control(self):
		bus1 = can.Bus(interface = "virtual", channel = 0)
		bus2 = can.Bus(interface = "virtual", channel = 0)
		dictionary = ObjectDictionary()
		node = Node("a", 0x0A, dictionary)
		examinee = NMTSlave(node)
		network = Network()
		
		network.attach(bus1)
		node.attach(network)
		examinee.attach()
		
		examinee.add_callback("start", self.__callback_start)
		examinee.add_callback("stop", self.__callback_stop)
		examinee.add_callback("pre-operational", self.__callback_pre_operational)
		examinee.add_callback("reset-application", self.__callback_reset_application)
		examinee.add_callback("reset-communication", self.__callback_reset_communication)
		
		#### Test step: Missing data
		message = can.Message(arbitration_id = 0x700 + node.id, is_extended_id = False, data = [])
		bus2.send(message)
		time.sleep(0.001)
		
		#### Test step: Wrong RTR length
		message = can.Message(arbitration_id = 0x700 + node.id, is_extended_id = False, is_remote_frame = True, dlc = 2)
		bus2.send(message)
		time.sleep(0.001)
		
		#### Test step: Error control should not respond in initialization state
		self.assertEqual(examinee.state, INITIALIZATION)
		
		message = can.Message(arbitration_id = 0x700 + node.id, is_extended_id = False, is_remote_frame = True, dlc = 1)
		bus2.send(message)
		
		# No response after 1 second
		message = bus2.recv(1)
		self.assertEqual(message, None)
		
		#### Test step: Check toggle bit in operational state
		# Application somewhen finishes start-up and changes the node's nmt state to pre-operational
		examinee.state = PRE_OPERATIONAL
		
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x01\x0A")
		bus2.send(message)
		time.sleep(0.001)
		self.assertEqual(examinee.state, OPERATIONAL)
		
		message = can.Message(arbitration_id = 0x700 + node.id, is_extended_id = False, is_remote_frame = True, dlc = 1)
		bus2.send(message)
		
		message = bus2.recv(1)
		self.assertEqual(message.arbitration_id, 0x700 + node.id)
		self.assertEqual(message.is_remote_frame, False)
		self.assertEqual(message.data, b"\x05")
		
		message = can.Message(arbitration_id = 0x700 + node.id, is_extended_id = False, is_remote_frame = True, dlc = 1)
		bus2.send(message)
		
		message = bus2.recv(1)
		self.assertEqual(message.arbitration_id, 0x700 + node.id)
		self.assertEqual(message.is_remote_frame, False)
		self.assertEqual(message.data, b"\x85")
		
		message = can.Message(arbitration_id = 0x700 + node.id, is_extended_id = False, is_remote_frame = True, dlc = 1)
		bus2.send(message)
		
		message = bus2.recv(1)
		self.assertEqual(message.arbitration_id, 0x700 + node.id)
		self.assertEqual(message.is_remote_frame, False)
		self.assertEqual(message.data, b"\x05")
		
		#### Test step: Reset communication - toggle bit should be reset to 0.
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x82\x0A")
		bus2.send(message)
		time.sleep(0.001)
		self.assertEqual(examinee.state, PRE_OPERATIONAL)
		
		message = can.Message(arbitration_id = 0x700 + node.id, is_extended_id = False, is_remote_frame = True, dlc = 1)
		bus2.send(message)
		
		message = bus2.recv(1)
		self.assertEqual(message.arbitration_id, 0x700 + node.id)
		self.assertEqual(message.is_remote_frame, False)
		self.assertEqual(message.data, b"\x7F")
		
		# The next error control response would be 0xFF. But we reset communication (and the toggle bit) now.
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x82\x0A")
		bus2.send(message)
		time.sleep(0.001)
		self.assertEqual(examinee.state, PRE_OPERATIONAL)
		
		message = can.Message(arbitration_id = 0x700 + node.id, is_extended_id = False, is_remote_frame = True, dlc = 1)
		bus2.send(message)
		
		message = bus2.recv(1)
		self.assertEqual(message.arbitration_id, 0x700 + node.id)
		self.assertEqual(message.is_remote_frame, False)
		self.assertEqual(message.data, b"\x7F")
		
		message = can.Message(arbitration_id = 0x700 + node.id, is_extended_id = False, is_remote_frame = True, dlc = 1)
		bus2.send(message)
		
		message = bus2.recv(1)
		self.assertEqual(message.arbitration_id, 0x700 + node.id)
		self.assertEqual(message.is_remote_frame, False)
		self.assertEqual(message.data, b"\xFF")
		
		message = can.Message(arbitration_id = 0x700 + node.id, is_extended_id = False, is_remote_frame = True, dlc = 1)
		bus2.send(message)
		
		message = bus2.recv(1)
		self.assertEqual(message.arbitration_id, 0x700 + node.id)
		self.assertEqual(message.is_remote_frame, False)
		self.assertEqual(message.data, b"\x7F")
		
		#### Test step: Setting state by application
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x81\x0A")
		bus2.send(message)
		time.sleep(0.001)
		self.assertEqual(examinee.state, PRE_OPERATIONAL)
		
		examinee.state = OPERATIONAL
		self.assertEqual(examinee.state, OPERATIONAL)
		
		message = can.Message(arbitration_id = 0x700 + node.id, is_extended_id = False, is_remote_frame = True, dlc = 1)
		bus2.send(message)
		
		message = bus2.recv(1)
		self.assertEqual(message.arbitration_id, 0x700 + node.id)
		self.assertEqual(message.is_remote_frame, False)
		self.assertEqual(message.data, b"\x05")
		
		#### Test step: Send heartbeat message
		examinee.send_heartbeat()
		
		message = bus2.recv(1)
		self.assertEqual(message.arbitration_id, 0x700 + node.id)
		self.assertEqual(message.is_remote_frame, False)
		self.assertEqual(message.data, b"\x05")
		
		examinee.send_heartbeat()
		
		message = bus2.recv(1)
		self.assertEqual(message.arbitration_id, 0x700 + node.id)
		self.assertEqual(message.is_remote_frame, False)
		self.assertEqual(message.data, b"\x05")
		
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
		examinee = NMTSlave(node)
		network = Network()
		
		network.attach(bus1)
		node.attach(network)
		examinee.attach()
		
		cb = Mock()
		examinee.add_callback("guarding", cb)
		
		test_data = [-1.0, 0.0]
		for value in test_data:
			with self.subTest(value):
				with self.assertRaises(ValueError):
					examinee.start_heartbeat(value)
		
		#### Test step 1: Starting heartbeat in initialization state and switching state afterwards. No message should be send until pre-operational state is set. 
		examinee.state = INITIALIZATION
		
		examinee.start_heartbeat(0.2)
		start_time = time.time()
		
		time.sleep(0.2 + start_time - time.time())
		
		message = bus2.recv(0.1)
		self.assertEqual(message, None)
		
		# No message until the state is set to pre-operational.
		
		examinee.state = PRE_OPERATIONAL
		
		# First message should be boot-up message
		message = bus2.recv(0.1)
		self.assertEqual(message.arbitration_id, 0x700 + node.id)
		self.assertEqual(message.is_remote_frame, False)
		self.assertEqual(message.data, b"\x00")
		
		time.sleep(0.5 + start_time - time.time())
		
		# Next message should indicate pre-operational state.
		message = bus2.recv(0.1)
		self.assertEqual(message.arbitration_id, 0x700 + node.id)
		self.assertEqual(message.is_remote_frame, False)
		self.assertEqual(message.data, b"\x7F")
		
		# Stop heartbeat functionality
		examinee.stop()
		
		time.sleep(0.7 + start_time - time.time())
		
		message = bus2.recv(0.1)
		self.assertEqual(message, None)
		
		# Start heartbeat functionality again. Now the node is in pre-operational state already.
		examinee.start_heartbeat(0.2)
		
		message = bus2.recv(0.1)
		self.assertEqual(message.arbitration_id, 0x700 + node.id)
		self.assertEqual(message.is_remote_frame, False)
		self.assertEqual(message.data, b"\x7F")
		
		# Stop heartbeat functionality
		examinee.stop()
		
		time.sleep(0.2)
		
		message = bus2.recv(0.1)
		self.assertEqual(message, None)
		
		# The callback is not used in heartbeat, so it should not have been called
		cb.assert_not_called()
		
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
		examinee = NMTSlave(node)
		network = Network()
		
		network.attach(bus1)
		node.attach(network)
		examinee.attach()
		
		cb = Mock()
		examinee.add_callback("guarding", cb)
		
		test_data = [(-1, 1), (0, 1), (1, -1), (1, 0)]
		for guard_time, life_time_factor in test_data:
			with self.subTest("guard_time=" + str(guard_time) + ", life_time_factor=" + str(life_time_factor)):
				with self.assertRaises(ValueError):
					examinee.start_guarding(guard_time, life_time_factor)
		
		examinee.state = PRE_OPERATIONAL
		
		examinee.start_guarding(0.2, 2)
		start_time = time.time()
		
		# Interval 0, Trigger guarding with the first RTR
		
		message = can.Message(arbitration_id = 0x700 + node.id, is_remote_frame = True, dlc = 1)
		bus2.send(message)
		
		time.sleep(0.05 + start_time - time.time())
		
		message = bus2.recv(0.1)
		self.assertEqual(message.arbitration_id, 0x700 + node.id)
		self.assertEqual(message.is_remote_frame, False)
		self.assertEqual(message.data, b"\x7F")
		
		cb.assert_not_called()
		
		time.sleep(0.15 + start_time - time.time())
		
		# Interval 1, t = 0.15
		message = can.Message(arbitration_id = 0x700 + node.id, is_remote_frame = True, dlc = 1)
		bus2.send(message)
		
		time.sleep(0.2 + start_time - time.time())
		
		message = bus2.recv(0.1)
		self.assertEqual(message.arbitration_id, 0x700 + node.id)
		self.assertEqual(message.is_remote_frame, False)
		self.assertEqual(message.data, b"\xFF")
		
		cb.assert_not_called()
		
		time.sleep(0.35 + start_time - time.time())
		
		# Interval 2, t = 0.35, no RTR
		cb.assert_not_called()
		
		time.sleep(0.55 + start_time - time.time())
		
		cb.assert_not_called()
		# Interval 3, t = 0.55, no RTR, now the callback should be called
		
		time.sleep(0.75 + start_time - time.time())
		
		cb.assert_called_with("guarding", examinee)
		
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
	
	def __callback_start(self, event, service, *args):
		service.state = OPERATIONAL
	
	def __callback_stop(self, event, service, *args):
		service.state = STOPPED
	
	def __callback_pre_operational(self, event, service, *args):
		service.state = PRE_OPERATIONAL
	
	def __callback_reset_application(self, event, service, *args):
		service.state = INITIALIZATION
		service.state = PRE_OPERATIONAL
	
	def __callback_reset_communication(self, event, service, *args):
		service.state = INITIALIZATION
		service.state = PRE_OPERATIONAL
	
	def __callback_raises(self, event, service, *args):
		raise Exception()


if __name__ == "__main__":
	unittest.main()
