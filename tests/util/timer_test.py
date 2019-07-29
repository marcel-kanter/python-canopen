import unittest
import time
import canopen.util


class TimerTest(unittest.TestCase):
	def test_all(self):
		examinee = canopen.util.Timer()
		time.sleep(0.1)
		examinee.start()
		time.sleep(0.1)
		examinee.start()
		time.sleep(0.1)
		examinee.stop()
		time.sleep(0.1)
		self.assertFalse(examinee.is_alive())


if __name__ == "__main__":
	unittest.main()
