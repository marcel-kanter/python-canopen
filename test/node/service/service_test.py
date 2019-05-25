import unittest
import canopen.node.service


class ServiceTestCase(unittest.TestCase):
	def test_init(self):
		canopen.node.service.Service()
	
	def test_attach_detach(self):
		network = canopen.Network()
		node1 = canopen.Node("a", 1)
		node2 = canopen.Node("b", 2)
		service = canopen.node.service.Service()
		
		node1.attach(network)
		node2.attach(network)
		
		with self.assertRaises(TypeError):
			service.attach(None)
		
		service.attach(node1)
		
		with self.assertRaises(ValueError):
			service.attach(node1)
		
		service.attach(node2)
		
		service.detach()
		
		node1.detach()
		node2.detach()


if __name__ == "__main__":
	unittest.main()
