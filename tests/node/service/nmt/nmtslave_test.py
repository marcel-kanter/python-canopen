import unittest
from unittest.mock import Mock
import time
import can
import canopen.node.service
import canopen.nmt.states


class NMTSlaveTestCase(unittest.TestCase):
	def test_init(self):
		nmt = canopen.node.service.NMTSlave()
		self.assertEqual(nmt.state, canopen.nmt.states.INITIALIZATION)
		
		#### Test step: Check if unallowed values raise a ValueError
		with self.assertRaises(ValueError):
			nmt.state = 0x11
		
		#### Test step: Check if only transition to pre-operational state is allowed
		with self.assertRaises(ValueError):
			nmt.state = canopen.nmt.states.STOPPED
		
		with self.assertRaises(ValueError):
			nmt.state = canopen.nmt.states.OPERATIONAL
		
		nmt.state = canopen.nmt.states.PRE_OPERATIONAL
		self.assertEqual(nmt.state, canopen.nmt.states.PRE_OPERATIONAL)
		
		#### Test step: Check if all transitions are possible - the test cycles one time completely through all states in both directions
		test_data = [canopen.nmt.states.PRE_OPERATIONAL, canopen.nmt.states.OPERATIONAL, canopen.nmt.states.STOPPED, canopen.nmt.states.PRE_OPERATIONAL, canopen.nmt.states.STOPPED, canopen.nmt.states.OPERATIONAL, canopen.nmt.states.PRE_OPERATIONAL]
		for value in test_data:
			with self.subTest(value = value):
				nmt.state = value
				self.assertEqual(nmt.state, value)
	
	def test_callback(self):
		examinee = canopen.node.service.NMTSlave()
		
		with self.assertRaises(TypeError):
			examinee.add_callback("start", None)
		
		with self.assertRaises(ValueError):
			examinee.add_callback("xxx", self.__callback_start)
		
		m_start = Mock()
		m_stop = Mock()
		m_pre_operational = Mock()
		m_reset_application = Mock()
		m_reset_communication = Mock()
		m_raises = Mock()
		
		#### Test step: add callback
		examinee.add_callback("start", m_start)
		examinee.add_callback("stop", m_stop)
		examinee.add_callback("pre-operational", m_pre_operational)
		examinee.add_callback("reset-communication", m_reset_communication)
		examinee.add_callback("reset-application", m_reset_application)
		
		examinee.add_callback("start", m_raises)
		
		#### Test step: notify
		with self.assertRaises(ValueError):
			examinee.notify("xxx", examinee)
		
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
		
		#### Test step: remove callback
		with self.assertRaises(TypeError):
			examinee.remove_callback("start", None)
		
		with self.assertRaises(ValueError):
			examinee.remove_callback("xxx", m_start)
		
		with self.assertRaises(ValueError):
			examinee.remove_callback("start", self.test_callback)
		
		examinee.remove_callback("start", m_start)
		examinee.remove_callback("stop", m_stop)
		examinee.remove_callback("pre-operational", m_pre_operational)
		examinee.remove_callback("reset-application", m_reset_application)
		examinee.remove_callback("reset-communication", m_reset_communication)
		examinee.remove_callback("start", m_raises)
	
	def test_attach_detach(self):
		network = canopen.Network()
		dictionary = canopen.ObjectDictionary()
		node1 = canopen.Node("a", 1, dictionary)
		node2 = canopen.Node("b", 2, dictionary)
		examinee = canopen.node.service.NMTSlave()
		
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
	
	def test_node_control(self):
		bus = can.Bus(interface = "virtual", channel = 0, receive_own_messages = True)
		network = canopen.Network()
		dictionary = canopen.ObjectDictionary()
		node = canopen.LocalNode("a", 0x0A, dictionary)
		
		node.nmt.add_callback("start", self.__callback_start)
		node.nmt.add_callback("stop", self.__callback_stop)
		node.nmt.add_callback("pre-operational", self.__callback_pre_operational)
		node.nmt.add_callback("reset-application", self.__callback_reset_application)
		
		network.attach(bus)
		network.add(node)
		
		self.assertEqual(node.nmt.state, 0x00)
		
		#### Test step: Wrong data length
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x00")
		bus.send(message)
		time.sleep(0.001)
		self.assertEqual(node.nmt.state, canopen.nmt.states.INITIALIZATION)
		
		#### Test step: Wrong node id
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x01\x10")
		bus.send(message)
		time.sleep(0.001)
		self.assertEqual(node.nmt.state, canopen.nmt.states.INITIALIZATION)
		
		#### Test step: Unknown command with direct addressing
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x00\x0A")
		bus.send(message)
		time.sleep(0.001)
		self.assertEqual(node.nmt.state, canopen.nmt.states.INITIALIZATION)
		
		#### Test step: Unknwon command with broadcast
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x00\x00")
		bus.send(message)
		time.sleep(0.001)
		self.assertEqual(node.nmt.state, canopen.nmt.states.INITIALIZATION)
		
		#### Test step: Addressing with node id
		# Application somewhen finishes start-up and changes the node's nmt state to pre-operational
		node.nmt.state = canopen.nmt.states.PRE_OPERATIONAL
		
		# Start (enter NMT operational)
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x01\x0A")
		bus.send(message)
		time.sleep(0.001)
		self.assertEqual(node.nmt.state, canopen.nmt.states.OPERATIONAL)
		
		# Enter NMT pre-operational
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x80\x0A")
		bus.send(message)
		time.sleep(0.001)
		self.assertEqual(node.nmt.state, canopen.nmt.states.PRE_OPERATIONAL)
		
		# Enter NMT reset application
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x81\x0A")
		bus.send(message)
		time.sleep(0.001)
		self.assertEqual(node.nmt.state, canopen.nmt.states.PRE_OPERATIONAL)
		
		# Stop (enter to NMT stopped)
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x02\x0A")
		bus.send(message)
		time.sleep(0.001)
		self.assertEqual(node.nmt.state, canopen.nmt.states.STOPPED)
		
		# Enter NMT reset communication
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x82\x0A")
		bus.send(message)
		time.sleep(0.001)
		self.assertEqual(node.nmt.state, canopen.nmt.states.PRE_OPERATIONAL)
		
		#### Test step: Addressing with broadcast
		# Start (enter NMT operational)
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x01\x00")
		bus.send(message)
		time.sleep(0.001)
		self.assertEqual(node.nmt.state, canopen.nmt.states.OPERATIONAL)
		
		# Enter NMT pre-operational
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x80\x00")
		bus.send(message)
		time.sleep(0.001)
		self.assertEqual(node.nmt.state, canopen.nmt.states.PRE_OPERATIONAL)
		
		# Enter NMT reset application
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x81\x00")
		bus.send(message)
		time.sleep(0.001)
		self.assertEqual(node.nmt.state, canopen.nmt.states.PRE_OPERATIONAL)
		
		# Stop (enter to NMT stopped)
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x02\x00")
		bus.send(message)
		time.sleep(0.001)
		self.assertEqual(node.nmt.state, canopen.nmt.states.STOPPED)
		
		# Enter NMT reset communication
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x82\x00")
		bus.send(message)
		time.sleep(0.001)
		self.assertEqual(node.nmt.state, canopen.nmt.states.PRE_OPERATIONAL)
		
		network.detach()
		bus.shutdown()
	
	def test_error_control(self):
		bus1 = can.Bus(interface = "virtual", channel = 0)
		bus2 = can.Bus(interface = "virtual", channel = 0)
		network = canopen.Network()
		dictionary = canopen.ObjectDictionary()
		node = canopen.LocalNode("a", 0x0A, dictionary)
		
		node.nmt.add_callback("start", self.__callback_start)
		node.nmt.add_callback("stop", self.__callback_stop)
		node.nmt.add_callback("pre-operational", self.__callback_pre_operational)
		node.nmt.add_callback("reset-application", self.__callback_reset_application)
		
		network.attach(bus1)
		network.add(node)
		
		#### Test step: Missing data
		message = can.Message(arbitration_id = 0x700 + node.id, is_extended_id = False, data = [])
		bus2.send(message)
		time.sleep(0.001)
		
		#### Test step: Wrong RTR length
		message = can.Message(arbitration_id = 0x700 + node.id, is_extended_id = False, is_remote_frame = True, dlc = 2)
		bus2.send(message)
		time.sleep(0.001)
		
		#### Test step: Error control should not respond in initialization state
		self.assertEqual(node.nmt.state, canopen.nmt.states.INITIALIZATION)
		
		message = can.Message(arbitration_id = 0x700 + node.id, is_extended_id = False, is_remote_frame = True, dlc = 1)
		bus2.send(message)
		
		# No response after 1 second
		message = bus2.recv(1)
		self.assertEqual(message, None)
		
		#### Test step: Check toggle bit in operational state
		# Application somewhen finishes start-up and changes the node's nmt state to pre-operational
		node.nmt.state = canopen.nmt.states.PRE_OPERATIONAL
		
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x01\x0A")
		bus2.send(message)
		time.sleep(0.001)
		self.assertEqual(node.nmt.state, canopen.nmt.states.OPERATIONAL)
		
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
		self.assertEqual(node.nmt.state, canopen.nmt.states.PRE_OPERATIONAL)
		
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
		self.assertEqual(node.nmt.state, canopen.nmt.states.PRE_OPERATIONAL)
		
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
		self.assertEqual(node.nmt.state, canopen.nmt.states.PRE_OPERATIONAL)
		
		node.nmt.state = canopen.nmt.states.OPERATIONAL
		self.assertEqual(node.nmt.state, canopen.nmt.states.OPERATIONAL)
		
		message = can.Message(arbitration_id = 0x700 + node.id, is_extended_id = False, is_remote_frame = True, dlc = 1)
		bus2.send(message)
		
		message = bus2.recv(1)
		self.assertEqual(message.arbitration_id, 0x700 + node.id)
		self.assertEqual(message.is_remote_frame, False)
		self.assertEqual(message.data, b"\x05")
		
		#### Test step: Send heartbeat message
		node.nmt.send_heartbeat()
		
		message = bus2.recv(1)
		self.assertEqual(message.arbitration_id, 0x700 + node.id)
		self.assertEqual(message.is_remote_frame, False)
		self.assertEqual(message.data, b"\x05")
		
		node.nmt.send_heartbeat()
		
		message = bus2.recv(1)
		self.assertEqual(message.arbitration_id, 0x700 + node.id)
		self.assertEqual(message.is_remote_frame, False)
		self.assertEqual(message.data, b"\x05")
		
		network.detach()
		bus1.shutdown()
		bus2.shutdown()
	
	def test_heartbeat(self):
		bus1 = can.Bus(interface = "virtual", channel = 0)
		bus2 = can.Bus(interface = "virtual", channel = 0)
		network = canopen.Network()
		dictionary = canopen.ObjectDictionary()
		node = canopen.LocalNode("a", 0x0A, dictionary)
		
		network.attach(bus1)
		network.add(node)
		
		test_data = [-1.0, 0.0]
		for value in test_data:
			with self.subTest(value):
				with self.assertRaises(ValueError):
					node.nmt.start_heartbeat(value)
		
		node.nmt.state = canopen.nmt.states.PRE_OPERATIONAL
		
		node.nmt.start_heartbeat(0.2)
		time.sleep(0.05)
		
		message = bus2.recv(1)
		self.assertEqual(message.arbitration_id, 0x700 + node.id)
		self.assertEqual(message.is_remote_frame, False)
		self.assertEqual(message.data, b"\x7F")
		
		time.sleep(0.2)
		
		message = bus2.recv(1)
		self.assertEqual(message.arbitration_id, 0x700 + node.id)
		self.assertEqual(message.is_remote_frame, False)
		self.assertEqual(message.data, b"\x7F")
		
		del network[node.id]
		network.detach()
		bus1.shutdown()
		bus2.shutdown()
	
	def test_guarding(self):
		bus1 = can.Bus(interface = "virtual", channel = 0)
		bus2 = can.Bus(interface = "virtual", channel = 0)
		network = canopen.Network()
		dictionary = canopen.ObjectDictionary()
		node = canopen.LocalNode("a", 0x0A, dictionary)
		
		network.attach(bus1)
		network.add(node)
		
		test_data = [-1.0, 0.0]
		for value in test_data:
			with self.subTest(value):
				with self.assertRaises(ValueError):
					node.nmt.start_guarding(value)
		
		node.nmt.state = canopen.nmt.states.PRE_OPERATIONAL
		
		node.nmt.start_guarding(0.2)
		
		del network[node.id]
		network.detach()
		bus1.shutdown()
		bus2.shutdown()
	
	def __callback_start(self, event, service, *args):
		service.node.nmt.state = canopen.nmt.states.OPERATIONAL
	
	def __callback_stop(self, event, service, *args):
		service.node.nmt.state = canopen.nmt.states.STOPPED
	
	def __callback_pre_operational(self, event, service, *args):
		service.node.nmt.state = canopen.nmt.states.PRE_OPERATIONAL
	
	def __callback_reset_application(self, event, service, *args):
		service.node.nmt.state = canopen.nmt.states.PRE_OPERATIONAL
	
	def __callback_raises(self, event, service, *args):
		raise Exception()


if __name__ == "__main__":
	unittest.main()
