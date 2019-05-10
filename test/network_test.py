import unittest
import canopen
import can


class NetworkTestCase(unittest.TestCase):
	def test_init(self):
		network = canopen.Network()
		bus = can.Bus(interface = "virtual", channel = 0)
		
		network.connect(bus)
		
		network.connect(bus)
		
		network.disconnect()
		
		bus.shutdown()


if __name__ == "__main__":
	unittest.main()
