import unittest
import canopen


class NetworkTestCase(unittest.TestCase):
	def test_init(self):
		network = canopen.Network()


if __name__ == "__main__":
	unittest.main()
