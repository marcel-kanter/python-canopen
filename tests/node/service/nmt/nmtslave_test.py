import unittest
from unittest.mock import Mock
import time
import can
import canopen.node.service
import canopen.nmt.states
from more_itertools.more import side_effect


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
		
		#### Test step: Check if all transitions are possible
		nmt.state = canopen.nmt.states.PRE_OPERATIONAL
		self.assertEqual(nmt.state, canopen.nmt.states.PRE_OPERATIONAL)
		
		nmt.state = canopen.nmt.states.OPERATIONAL
		self.assertEqual(nmt.state, canopen.nmt.states.OPERATIONAL)
		
		nmt.state = canopen.nmt.states.STOPPED
		self.assertEqual(nmt.state, canopen.nmt.states.STOPPED)
		
		nmt.state = canopen.nmt.states.PRE_OPERATIONAL
		self.assertEqual(nmt.state, canopen.nmt.states.PRE_OPERATIONAL)
		
		nmt.state = canopen.nmt.states.STOPPED
		self.assertEqual(nmt.state, canopen.nmt.states.STOPPED)
		
		nmt.state = canopen.nmt.states.OPERATIONAL
		self.assertEqual(nmt.state, canopen.nmt.states.OPERATIONAL)
		
		nmt.state = canopen.nmt.states.PRE_OPERATIONAL
		self.assertEqual(nmt.state, canopen.nmt.states.PRE_OPERATIONAL)
	
	def test_callback(self):
		examinee = canopen.node.service.NMTSlave()
		
		with self.assertRaises(TypeError):
			examinee.add_callback("start", None)
		
		with self.assertRaises(ValueError):
			examinee.add_callback("xxx", self.__callback_start)
		
		m_start = Mock(side_effect = self.__callback_start)
		m_stop = Mock(side_effect = self.__callback_start)
		m_pause = Mock(side_effect = self.__callback_start)
		m_reset = Mock(side_effect = self.__callback_start)
		m_raises = Mock(side_effect = self.__callback_raises)
		
		#### Test step: add callback
		examinee.add_callback("start", m_start)
		examinee.add_callback("stop", m_stop)
		examinee.add_callback("pause", m_pause)
		examinee.add_callback("reset", m_reset)
		
		examinee.add_callback("start", m_raises)
		
		#### Test step: notify
		with self.assertRaises(ValueError):
			examinee.notify("xxx", None)
		
		examinee.notify("start", None)
		m_start.assert_called_once()
		m_stop.assert_not_called()
		m_pause.assert_not_called()
		m_reset.assert_not_called()
		m_raises.assert_called_once()
		
		examinee.notify("stop", None)
		m_start.assert_called_once()
		m_stop.assert_called_once()
		m_pause.assert_not_called()
		m_reset.assert_not_called()
		m_raises.assert_called_once()
		
		examinee.notify("pause", None)
		m_start.assert_called_once()
		m_stop.assert_called_once()
		m_pause.assert_called_once()
		m_reset.assert_not_called()
		m_raises.assert_called_once()
		
		examinee.notify("reset", None)
		m_start.assert_called_once()
		m_stop.assert_called_once()
		m_pause.assert_called_once()
		m_reset.assert_called_once()
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
		examinee.remove_callback("pause", m_pause)
		examinee.remove_callback("reset", m_reset)
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
		node.nmt.add_callback("pause", self.__callback_pause)
		node.nmt.add_callback("reset", self.__callback_reset)
		
		network.attach(bus)
		network.append(node)
		
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
		node.nmt.add_callback("pause", self.__callback_pause)
		node.nmt.add_callback("reset", self.__callback_reset)
		
		network.attach(bus1)
		network.append(node)
		
		#### Test step: Missing data
		message = can.Message(arbitration_id = 0x70A, is_extended_id = False, data = [])
		bus2.send(message)
		time.sleep(0.001)
		
		#### Test step: Wrong RTR length
		message = can.Message(arbitration_id = 0x70A, is_extended_id = False, is_remote_frame = True, dlc = 2)
		bus2.send(message)
		time.sleep(0.001)
		
		#### Test step: Error control should not respond in initialization state
		self.assertEqual(node.nmt.state, canopen.nmt.states.INITIALIZATION)
		
		message = can.Message(arbitration_id = 0x70A, is_extended_id = False, is_remote_frame = True, dlc = 1)
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
		
		message = can.Message(arbitration_id = 0x70A, is_extended_id = False, is_remote_frame = True, dlc = 1)
		bus2.send(message)
		
		message = bus2.recv(1)
		self.assertEqual(message.arbitration_id, 0x70A)
		self.assertEqual(message.is_remote_frame, False)
		self.assertEqual(message.data, b"\x05")
		
		message = can.Message(arbitration_id = 0x70A, is_extended_id = False, is_remote_frame = True, dlc = 1)
		bus2.send(message)
		
		message = bus2.recv(1)
		self.assertEqual(message.arbitration_id, 0x70A)
		self.assertEqual(message.is_remote_frame, False)
		self.assertEqual(message.data, b"\x85")
		
		message = can.Message(arbitration_id = 0x70A, is_extended_id = False, is_remote_frame = True, dlc = 1)
		bus2.send(message)
		
		message = bus2.recv(1)
		self.assertEqual(message.arbitration_id, 0x70A)
		self.assertEqual(message.is_remote_frame, False)
		self.assertEqual(message.data, b"\x05")
		
		#### Test step: Reset communication - toggle bit should be reset to 0.
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x82\x0A")
		bus2.send(message)
		time.sleep(0.001)
		self.assertEqual(node.nmt.state, canopen.nmt.states.PRE_OPERATIONAL)
		
		message = can.Message(arbitration_id = 0x70A, is_extended_id = False, is_remote_frame = True, dlc = 1)
		bus2.send(message)
		
		message = bus2.recv(1)
		self.assertEqual(message.arbitration_id, 0x70A)
		self.assertEqual(message.is_remote_frame, False)
		self.assertEqual(message.data, b"\x7F")
		
		# The next error control response would be 0xFF. But we reset communication (and the toggle bit) now.
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x82\x0A")
		bus2.send(message)
		time.sleep(0.001)
		self.assertEqual(node.nmt.state, canopen.nmt.states.PRE_OPERATIONAL)
		
		message = can.Message(arbitration_id = 0x70A, is_extended_id = False, is_remote_frame = True, dlc = 1)
		bus2.send(message)
		
		message = bus2.recv(1)
		self.assertEqual(message.arbitration_id, 0x70A)
		self.assertEqual(message.is_remote_frame, False)
		self.assertEqual(message.data, b"\x7F")
		
		message = can.Message(arbitration_id = 0x70A, is_extended_id = False, is_remote_frame = True, dlc = 1)
		bus2.send(message)
		
		message = bus2.recv(1)
		self.assertEqual(message.arbitration_id, 0x70A)
		self.assertEqual(message.is_remote_frame, False)
		self.assertEqual(message.data, b"\xFF")
		
		message = can.Message(arbitration_id = 0x70A, is_extended_id = False, is_remote_frame = True, dlc = 1)
		bus2.send(message)
		
		message = bus2.recv(1)
		self.assertEqual(message.arbitration_id, 0x70A)
		self.assertEqual(message.is_remote_frame, False)
		self.assertEqual(message.data, b"\x7F")
		
		#### Test step: Setting state by application
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x81\x0A")
		bus2.send(message)
		time.sleep(0.001)
		self.assertEqual(node.nmt.state, canopen.nmt.states.PRE_OPERATIONAL)
		
		node.nmt.state = canopen.nmt.states.OPERATIONAL
		self.assertEqual(node.nmt.state, canopen.nmt.states.OPERATIONAL)
		
		message = can.Message(arbitration_id = 0x70A, is_extended_id = False, is_remote_frame = True, dlc = 1)
		bus2.send(message)
		
		message = bus2.recv(1)
		self.assertEqual(message.arbitration_id, 0x70A)
		self.assertEqual(message.is_remote_frame, False)
		self.assertEqual(message.data, b"\x05")
		
		#### Test step: Send heartbeat message
		node.nmt.send_heartbeat()
		
		message = bus2.recv(1)
		self.assertEqual(message.arbitration_id, 0x70A)
		self.assertEqual(message.is_remote_frame, False)
		self.assertEqual(message.data, b"\x05")
		
		node.nmt.send_heartbeat()
		
		message = bus2.recv(1)
		self.assertEqual(message.arbitration_id, 0x70A)
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
		network.append(node)
		
		node.nmt.send_heartbeat()
		node.nmt.state = canopen.nmt.states.PRE_OPERATIONAL
		node.nmt.start_heartbeat(0.2)
		
		time.sleep(0.05)
		
		message = bus2.recv(0.2)
		self.assertEqual(message.arbitration_id, 0x70A)
		self.assertEqual(message.is_remote_frame, False)
		self.assertEqual(message.data, b"\x00")
		
		time.sleep(0.2)
		
		message = bus2.recv(0.2)
		self.assertEqual(message.arbitration_id, 0x70A)
		self.assertEqual(message.is_remote_frame, False)
		self.assertEqual(message.data, b"\x7F")
		
		time.sleep(0.2)
		
		message = bus2.recv(0.2)
		self.assertEqual(message.arbitration_id, 0x70A)
		self.assertEqual(message.is_remote_frame, False)
		self.assertEqual(message.data, b"\x7F")
		
		node.nmt.stop_heartbeat()
		
		network.detach()
		bus1.shutdown()
		bus2.shutdown()
	
	def __callback_start(self, event, node, *args):
		node.nmt.state = canopen.nmt.states.OPERATIONAL
	
	def __callback_stop(self, event, node, *args):
		node.nmt.state = canopen.nmt.states.STOPPED
	
	def __callback_pause(self, event, node, *args):
		node.nmt.state = canopen.nmt.states.PRE_OPERATIONAL
	
	def __callback_reset(self, event, node, *args):
		node.nmt.state = canopen.nmt.states.PRE_OPERATIONAL
	
	def __callback_raises(self, event, node, *args):
		raise Exception()


if __name__ == "__main__":
	unittest.main()
