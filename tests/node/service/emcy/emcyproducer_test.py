import unittest
import canopen.node.service


class EMCYProducerTestCase(unittest.TestCase):
	def test_init(self):
		canopen.node.service.EMCYProducer()
	
	def test_attach_detach(self):
		dictionary = canopen.ObjectDictionary()
		network = canopen.Network()
		node1 = canopen.Node("a", 1, dictionary)
		node2 = canopen.Node("b", 2, dictionary)
		emcyproducer = canopen.node.service.EMCYProducer()
		
		node1.attach(network)
		node2.attach(network)
		
		with self.assertRaises(RuntimeError):
			emcyproducer.detach()
		
		with self.assertRaises(TypeError):
			emcyproducer.attach(None)
		
		emcyproducer.attach(node1)
		
		with self.assertRaises(ValueError):
			emcyproducer.attach(node1)
		
		emcyproducer.attach(node2)
		
		emcyproducer.detach()
		
		node1.detach()
		node2.detach()


if __name__ == "__main__":
	unittest.main()
