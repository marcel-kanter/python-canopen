import unittest
import canopen.node.service


class SDOServerTestCase(unittest.TestCase):
	def test_init(self):
		canopen.node.service.SDOServer()
	
	def test_attach_detach(self):
		network = canopen.Network()
		node1 = canopen.Node("a", 1)
		node2 = canopen.Node("b", 2)
		sdoserver = canopen.node.service.SDOServer()
		
		node1.attach(network)
		node2.attach(network)
		
		with self.assertRaises(TypeError):
			sdoserver.attach(None)
		
		sdoserver.attach(node1)
		
		with self.assertRaises(ValueError):
			sdoserver.attach(node1)
		
		sdoserver.attach(node2)
		
		sdoserver.detach()
		
		node1.detach()
		node2.detach()


if __name__ == "__main__":
	unittest.main()
