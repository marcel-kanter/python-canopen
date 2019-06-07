import unittest
import time
import can
import canopen.node.service


class NMTSlaveTestCase(unittest.TestCase):
	def test_init(self):
		nmt = canopen.node.service.NMTSlave()
		self.assertEqual(nmt.state, 0x00)
		
		#### Test step: Check if unallowed values raise a ValueError
		with self.assertRaises(ValueError):
			nmt.state = 0x11
		
		#### Test step: Check if only transition to pre-operational state is allowed
		with self.assertRaises(ValueError):
			nmt.state = 0x04
		
		with self.assertRaises(ValueError):
			nmt.state = 0x05
		
		nmt.state = 0x7F
		self.assertEqual(nmt.state, 0x7F)
		
		#### Test step: Check if all transitions are possible
		nmt.state = 0x7F
		self.assertEqual(nmt.state, 0x7F)
		
		nmt.state = 0x05
		self.assertEqual(nmt.state, 0x05)
		
		nmt.state = 0x04
		self.assertEqual(nmt.state, 0x04)
		
		nmt.state = 0x7F
		self.assertEqual(nmt.state, 0x7F)
		
		nmt.state = 0x04
		self.assertEqual(nmt.state, 0x04)
		
		nmt.state = 0x05
		self.assertEqual(nmt.state, 0x05)
		
		nmt.state = 0x7F
		self.assertEqual(nmt.state, 0x7F)
	
	def test_callback(self):
		nmt = canopen.node.service.NMTSlave()
		
		with self.assertRaises(TypeError):
			nmt.add_callback(None, "start")
		
		with self.assertRaises(ValueError):
			nmt.add_callback(self.__callback_start, "xxx")
		
		nmt.add_callback(self.__callback_start, "start")
		nmt.add_callback(self.__callback_stop, "stop")
		nmt.add_callback(self.__callback_pause, "pause")
		nmt.add_callback(self.__callback_reset, "reset")
		
		nmt.add_callback(self.__callback_raises, "start")
		
		with self.assertRaises(ValueError):
			nmt.notify("xxx")
		
		nmt.notify("start")
		
		with self.assertRaises(TypeError):
			nmt.remove_callback(None, "start")
		
		with self.assertRaises(ValueError):
			nmt.remove_callback(self.__callback_start, "xxx")
		
		nmt.remove_callback(self.__callback_start, "start")
		nmt.remove_callback(self.__callback_stop, "stop")
		nmt.remove_callback(self.__callback_pause, "pause")
		nmt.remove_callback(self.__callback_reset, "reset")
		
		nmt.remove_callback(self.__callback_raises, "start")
	
	def test_attach_detach(self):
		network = canopen.Network()
		dictionary = canopen.ObjectDictionary()
		node1 = canopen.Node("a", 1, dictionary)
		node2 = canopen.Node("b", 2, dictionary)
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
		dictionary = canopen.ObjectDictionary()
		node = canopen.LocalNode("a", 0x0A, dictionary)
		
		node.nmt.add_callback(self.__callback_start, "start")
		node.nmt.add_callback(self.__callback_stop, "stop")
		node.nmt.add_callback(self.__callback_pause, "pause")
		node.nmt.add_callback(self.__callback_reset, "reset")
		
		network.attach(bus)
		network.append(node)
		
		self.assertEqual(node.nmt.state, 0x00)
		
		#### Test step: Wrong data length
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x00")
		bus.send(message)
		time.sleep(0.001)
		self.assertEqual(node.nmt.state, 0x00)
		
		#### Test step: Wrong node id
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x01\x10")
		bus.send(message)
		time.sleep(0.001)
		self.assertEqual(node.nmt.state, 0x00)
		
		#### Test step: Unknown command with direct addressing
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x00\x0A")
		bus.send(message)
		time.sleep(0.001)
		self.assertEqual(node.nmt.state, 0x00)
		
		#### Test step: Unknwon command with broadcast
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x00\x00")
		bus.send(message)
		time.sleep(0.001)
		self.assertEqual(node.nmt.state, 0x00)
		
		#### Test step: Addressing with node id
		# Application somewhen finishes start-up and changes the node's nmt state to pre-operational
		node.nmt.state = 0x7F
		
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
		
		#### Test step: Addressing with broadcast
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
		dictionary = canopen.ObjectDictionary()
		node = canopen.LocalNode("a", 0x0A, dictionary)
		
		node.nmt.add_callback(self.__callback_start, "start")
		node.nmt.add_callback(self.__callback_stop, "stop")
		node.nmt.add_callback(self.__callback_pause, "pause")
		node.nmt.add_callback(self.__callback_reset, "reset")
		
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
		self.assertEqual(node.nmt.state, 0x00)
		
		message = can.Message(arbitration_id = 0x70A, is_extended_id = False, is_remote_frame = True, dlc = 1)
		bus2.send(message)
		
		# No response after 1 second
		message = bus2.recv(1)
		self.assertEqual(message, None)
		
		#### Test step: Check toggle bit in operational state
		# Application somewhen finishes start-up and changes the node's nmt state to pre-operational
		node.nmt.state = 0x7F
		
		message = can.Message(arbitration_id = 0x000, is_extended_id = False, data = b"\x01\x0A")
		bus2.send(message)
		time.sleep(0.001)
		self.assertEqual(node.nmt.state, 0x05)
		
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
		self.assertEqual(node.nmt.state, 0x7F)
		
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
		self.assertEqual(node.nmt.state, 0x7F)
		
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
		self.assertEqual(node.nmt.state, 0x7F)
		
		node.nmt.state = 0x05
		self.assertEqual(node.nmt.state, 0x05)
		
		message = can.Message(arbitration_id = 0x70A, is_extended_id = False, is_remote_frame = True, dlc = 1)
		bus2.send(message)
		
		message = bus2.recv(1)
		self.assertEqual(message.arbitration_id, 0x70A)
		self.assertEqual(message.is_remote_frame, False)
		self.assertEqual(message.data, b"\x05")
		
		network.detach()
		bus1.shutdown()
		bus2.shutdown()
	
	def __callback_start(self, nmt):
		nmt.state = 0x05
	
	def __callback_stop(self, nmt):
		nmt.state = 0x04
	
	def __callback_pause(self, nmt):
		nmt.state = 0x7F
	
	def __callback_reset(self, nmt):
		nmt.state = 0x7F
	
	def __callback_raises(self, nmt):
		raise Exception()


if __name__ == "__main__":
	unittest.main()
