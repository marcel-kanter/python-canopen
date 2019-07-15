import unittest
import struct
import time
import can
import canopen
import canopen.objectdictionary


class RemoteNodeTestCase(unittest.TestCase):
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
			node.id = id
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
		network = canopen.Network()
		dictionary = canopen.ObjectDictionary()
		dictionary.append(canopen.objectdictionary.Record("rec", 0x1234))
		dictionary["rec"].append(canopen.objectdictionary.Variable("unicode", 0x1234, 0x0B, canopen.objectdictionary.UNICODE_STRING, "rw"))
		dictionary.append(canopen.objectdictionary.Variable("var", 0x5678, 0x00, canopen.objectdictionary.UNSIGNED32, "rw"))
		examinee = canopen.RemoteNode("examinee", 1, dictionary)
		
		network.attach(bus1)
		network.append(examinee)
		
		# TODO: Do something with set_data and get_data
		with self.assertRaises(NotImplementedError):
			examinee.set_data(0x5678, 0x00, 1234)
		with self.assertRaises(NotImplementedError):
			examinee.get_data(0x5678, 0x00)
		
		del network["examinee"]
		
		network.detach()
		bus1.shutdown()
		bus2.shutdown()


if __name__ == "__main__":
	unittest.main()
