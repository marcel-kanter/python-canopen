import unittest
from unittest.mock import Mock
import time
import canopen.util


class TimerTest(unittest.TestCase):
	def test_init(self):
		with self.assertRaises(ValueError):
			canopen.util.Timer(1.0, None)
		
		m = Mock()
		with self.assertRaises(ValueError):
			canopen.util.Timer(-1.0, m)
		
		examinee = canopen.util.Timer(1.0, m)
		self.assertTrue(examinee.is_alive())
		
		examinee.stop()
		time.sleep(0.01)
		self.assertFalse(examinee.is_alive())
		
		examinee = canopen.util.Timer(1.0, m, [10])
		self.assertTrue(examinee.is_alive())
		
		examinee.stop()
		time.sleep(0.01)
		self.assertFalse(examinee.is_alive())
		
		examinee = canopen.util.Timer(1.0, m, [10], {"a": 20})
		self.assertTrue(examinee.is_alive())
		
		examinee.stop()
		time.sleep(0.01)
		self.assertFalse(examinee.is_alive())
	
	def test_all(self):
		m = Mock()
		examinee = canopen.util.Timer(0.1, m, [10], {"a": 20})
		
		#### Test step: The timer should not start immediately after init
		time.sleep(0.2)
		m.assert_not_called()
		
		#### Test step: Start with interval from init
		m.reset_mock()
		examinee.start()
		time.sleep(0.08)
		m.assert_not_called()
		time.sleep(0.04)
		m.assert_called()
		
		#### Test step: Overwrite interval with new value
		m.reset_mock()
		examinee.start(0.2)
		time.sleep(0.18)
		m.assert_not_called()
		time.sleep(0.04)
		m.assert_called()
		
		#### Test step: Stop, no call at the end
		m.reset_mock()
		examinee.start(0.2)
		time.sleep(0.1)
		examinee.stop()
		time.sleep(0.2)
		m.assert_not_called()
		
		self.assertFalse(examinee.is_alive())


if __name__ == "__main__":
	unittest.main()
