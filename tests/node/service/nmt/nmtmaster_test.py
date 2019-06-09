import unittest
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
		nmt = canopen.node.service.NMTMaster()
		
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

if __name__ == "__main__":
	unittest.main()
