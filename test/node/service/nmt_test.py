import unittest
import canopen.node.service


class NMTSlaveTestCase(unittest.TestCase):
	def test_init(self):
		nmt = canopen.node.service.NMTSlave()
		self.assertEqual(nmt.state, 0)
		
		with self.assertRaises(AttributeError):
			nmt.state = 0
	
	def test_attach_detach(self):
		node1 = canopen.Node("a", 1)
		node2 = canopen.Node("b", 2)
		nmt = canopen.node.service.NMTSlave()
		
		with self.assertRaises(TypeError):
			nmt.attach(None)
		
		nmt.attach(node1)
		
		with self.assertRaises(ValueError):
			nmt.attach(node1)
		
		nmt.attach(node2)
		
		nmt.detach()

if __name__ == "__main__":
	unittest.main()
