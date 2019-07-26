import unittest
import time
import canopen.util


class TimerTest(unittest.TestCase):
	def test_init(self):
		examinee = canopen.util.Timer()
		time.sleep(0.01)
		examinee.stop()
		time.sleep(0.01)


if __name__ == "__main__":
	unittest.main()
