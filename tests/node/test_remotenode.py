import unittest
import sys
import struct
import threading
import time
import can
import canopen
import canopen.objectdictionary


class Vehicle(threading.Thread):
	def __init__(self, testcase, bus):
		threading.Thread.__init__(self, daemon = True)
		self._testcase = testcase
		self._bus = bus
		self._terminate = threading.Event()
	
	def stop(self):
		self._terminate.set()
	
	def run(self):
		try:
			network = canopen.Network()
			dictionary = canopen.ObjectDictionary()
			dictionary.add(canopen.objectdictionary.Variable("var", 0x5678, 0x00, canopen.objectdictionary.UNSIGNED32, "rw"))
			examinee = canopen.RemoteNode("examinee", 1, dictionary)
			
			network.attach(self._bus)
			network.add(examinee)
			
			examinee.set_data(0x5678, 0x00, 0x12345678)
			
			assert(examinee.get_data(0x5678, 0x00) == 1234)
			
			del network["examinee"]
			
			network.detach()
		except AssertionError:
			self._testcase.result.addFailure(self._testcase, sys.exc_info())
		except:
			self._testcase.result.addError(self._testcase, sys.exc_info())

class RemoteNodeTestCase(unittest.TestCase):
	def run(self, result = None):
		if result == None:
			self.result = self.defaultTestResult()
		else:
			self.result = result
		
		unittest.TestCase.run(self, self.result)
		
		return self.result
	
	def test_init(self):
		dictionary = canopen.ObjectDictionary()
		
		with self.assertRaises(ValueError):
			canopen.RemoteNode("n", 0, dictionary)
		with self.assertRaises(ValueError):
			canopen.RemoteNode("n", 128, dictionary)
		with self.assertRaises(TypeError):
			canopen.RemoteNode("n", 1, None)
		
		name = "n"
		node_id = 1
		node = canopen.RemoteNode(name, node_id, dictionary)
		
		self.assertEqual(node.dictionary, dictionary)
		self.assertEqual(node.id, node_id)
		self.assertEqual(node.name, name)
		self.assertEqual(node.network, None)
		
		with self.assertRaises(AttributeError):
			node.dictionary = dictionary
		with self.assertRaises(AttributeError):
			node.name = name
		with self.assertRaises(AttributeError):
			node.network = None
	
	def test_attach_detach(self):
		network1 = canopen.Network()
		network2 = canopen.Network()
		dictionary = canopen.ObjectDictionary()
		node = canopen.RemoteNode("n", 1, dictionary)
		
		with self.assertRaises(RuntimeError):
			node.detach()
		
		with self.assertRaises(TypeError):
			node.attach(None)
		
		node.attach(network1)
		
		self.assertEqual(node.network, network1)
		
		with self.assertRaises(ValueError):
			node.attach(network1)
		
		node.attach(network2)
		
		self.assertEqual(node.network, network2)
		
		node.detach()
	
	def test_data_access(self):
		bus1 = can.Bus(interface = "virtual", channel = 0)
		bus2 = can.Bus(interface = "virtual", channel = 0)
		
		vehicle = Vehicle(self, bus1)
		vehicle.start()
		
		#### Test step: set_data (download, expedited transfer)
		index = 0x5678
		subindex = 0x00
		value = 0x12345678
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x23, index, subindex, value))
		
		d = struct.pack("<BHBL", 0x60, index, subindex, 0x00000000)
		message_send = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message_send)
		
		#### Test step: get_data (Upload, expedited transfer)
		index = 0x5678
		subindex = 0x00
		value = 1234
		
		message_recv = bus2.recv(1)
		self.assertEqual(message_recv.arbitration_id, 0x601)
		self.assertEqual(message_recv.is_remote_frame, False)
		self.assertEqual(message_recv.data, struct.pack("<BHBL", 0x40, index, subindex, 0x00000000))
		
		d = struct.pack("<BHBL", 0x42, index, subindex, value)
		message_send = can.Message(arbitration_id = 0x581, is_extended_id = False, data = d)
		bus2.send(message_send)
		time.sleep(0.001)
		
		vehicle.join(1)
		
		bus1.shutdown()
		bus2.shutdown()


if __name__ == "__main__":
	unittest.main()
