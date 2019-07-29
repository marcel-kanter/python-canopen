import unittest
from unittest.mock import Mock
import time
import canopen.util


class TimerTest(unittest.TestCase):
	def test_init(self):
		with self.assertRaises(ValueError):
			canopen.util.Timer(None)
		
		m = Mock()
		examinee = canopen.util.Timer(m)
		self.assertTrue(examinee.is_alive())
		
		examinee.stop()
		time.sleep(0.01)
		self.assertFalse(examinee.is_alive())
		
		examinee = canopen.util.Timer(m, [10])
		self.assertTrue(examinee.is_alive())
		
		examinee.stop()
		time.sleep(0.01)
		self.assertFalse(examinee.is_alive())
		
		examinee = canopen.util.Timer(m, [10], {"a": 20})
		self.assertTrue(examinee.is_alive())
		
		examinee.stop()
		time.sleep(0.01)
		self.assertFalse(examinee.is_alive())
	
	def test_all(self):
		m = Mock()
		examinee = canopen.util.Timer(m, [10], {"a": 20})
		time.sleep(0.1)
		m.assert_not_called()
		
		examinee.start()
		time.sleep(0.1)
		m.assert_called()
		m.reset_mock()
		
		examinee.start()
		time.sleep(0.1)
		m.assert_called()
		m.reset_mock()
		
		examinee.stop()
		time.sleep(0.1)
		m.assert_not_called()
		
		self.assertFalse(examinee.is_alive())


if __name__ == "__main__":
	unittest.main()
