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
		t_start = time.time()
		self.assertEqual(examinee.start(), True)
		time.sleep(0.08)
		m.assert_not_called()
		time.sleep(0.04)
		m.assert_called()
		self.assertLess(time.time() - t_start, 0.15)
		
		#### Test step: Overwrite interval with new value
		m.reset_mock()
		t_start = time.time()
		self.assertEqual(examinee.start(0.15), True)
		time.sleep(0.13)
		m.assert_not_called()
		time.sleep(0.04)
		m.assert_called()
		self.assertLess(time.time() - t_start, 0.2)
		
		#### Test step: Cancel, start -> normal operation
		m.reset_mock()
		t_start = time.time()
		examinee.cancel()
		self.assertEqual(examinee.start(0.1), True)
		time.sleep(0.08)
		m.assert_not_called()
		time.sleep(0.04)
		m.assert_called()
		self.assertLess(time.time() - t_start, 0.15)
		
		m.reset_mock()
		t_start = time.time()
		examinee.cancel()
		time.sleep(0.05)
		self.assertEqual(examinee.start(0.1), True)
		time.sleep(0.08)
		m.assert_not_called()
		time.sleep(0.04)
		m.assert_called()
		self.assertLess(time.time() - t_start, 0.2)
		
		#### Test step: Start, cancel -> no call
		m.reset_mock()
		t_start = time.time()
		examinee.start(0.1)
		time.sleep(0.08)
		examinee.cancel()
		time.sleep(0.05)
		m.assert_not_called()
		self.assertLess(time.time() - t_start, 0.15)
		
		m.reset_mock()
		t_start = time.time()
		examinee.start(0.1)
		examinee.cancel()
		time.sleep(0.15)
		m.assert_not_called()
		self.assertLess(time.time() - t_start, 0.2)
		
		#### Test step: Start, start, cancel -> no call
		m.reset_mock()
		t_start = time.time()
		self.assertEqual(examinee.start(0.1), True)
		time.sleep(0.03)
		self.assertEqual(examinee.start(0.1), False)
		time.sleep(0.03)
		examinee.cancel()
		time.sleep(0.05)
		m.assert_not_called()
		self.assertLess(time.time() - t_start, 0.15)
		
		#### Test step: Start, cancel, start -> normal
		m.reset_mock()
		t_start = time.time()
		examinee.start(0.1)
		time.sleep(0.05)
		examinee.cancel()
		time.sleep(0.1)
		m.assert_not_called()
		examinee.start(0.1)
		time.sleep(0.08)
		m.assert_not_called()
		time.sleep(0.04)
		m.assert_called()
		self.assertLess(time.time() - t_start, 0.3)
		
		#### Test step: Stop, no call at the end
		m.reset_mock()
		t_start = time.time()
		examinee.start(0.2)
		time.sleep(0.1)
		examinee.stop()
		time.sleep(0.2)
		m.assert_not_called()
		self.assertFalse(examinee.is_alive())
		self.assertLess(time.time() - t_start, 0.35)


if __name__ == "__main__":
	unittest.main()
