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
		#### Test step: Init should leave the timer in a triggerable state
		cb = Mock()
		examinee = canopen.util.Timer(cb)
		examinee.start(0.1)
		
		time.sleep(0.15)
		cb.assert_called()
		
		del examinee
		del cb
		
		m = Mock()
		
		#### Test step: The timer cycle should not start immediately after init
		examinee = canopen.util.Timer(m, [10], {"a": 20})
		
		time.sleep(0.2)
		m.assert_not_called()
		
		#### Test step: Invalid interval
		with self.assertRaises(ValueError):
			examinee.start(-0.1)
		
		#### Test step: Start with interval from init
		m.reset_mock()
		t_start = time.time()
		self.assertEqual(examinee.start(0.1), True)
		time.sleep(0.08)
		m.assert_not_called()
		time.sleep(0.04)
		m.assert_called()
		self.assertLess(time.time() - t_start, 0.15)
		
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
		
		m.reset_mock()
		t_start = time.time()
		examinee.start(0.1)
		time.sleep(0.05)
		examinee.cancel()
		m.assert_not_called()
		examinee.start(0.1)
		time.sleep(0.08)
		m.assert_not_called()
		time.sleep(0.04)
		m.assert_called()
		self.assertLess(time.time() - t_start, 0.3)
		
		#### Test step: periodic mode
		m.reset_mock()
		t_start = time.time()
		examinee.start(0.1, True)
		time.sleep(0.05)
		m.assert_not_called()
		time.sleep(0.1)
		m.assert_called()
		m.reset_mock()
		time.sleep(0.1)
		m.assert_called()
		m.reset_mock()
		time.sleep(0.1)
		m.assert_called()
		m.reset_mock()
		examinee.cancel()
		time.sleep(0.1)
		m.assert_not_called()
		
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
		
		del examinee
		del m
		
		#### Test step: Cancel inside callback
		m = Mock(side_effect = self.stoptimer_callback)
		self.counter = 0
		self.examinee = canopen.util.Timer(m, [self])
		
		self.examinee.start(0.05, True)
		time.sleep(0.18)
		self.assertEqual(self.counter, 3)
		# Callback should have incremented counter to 3 and canceled the timer - counter should not increment any more
		time.sleep(0.2)
		self.assertEqual(self.counter, 3)
		
		# Start timer again
		self.counter = 0
		self.examinee.start(0.05, True)
		time.sleep(0.18)
		self.assertEqual(self.counter, 3)
		# Callback should have incremented counter to 3 and canceled the timer - counter should not increment any more
		time.sleep(0.2)
		self.assertEqual(self.counter, 3)
		
		del self.examinee
		del m
	
	def stoptimer_callback(self, testcase):
		testcase.counter += 1
		if testcase.counter == 3:
			testcase.examinee.cancel()


if __name__ == "__main__":
	unittest.main()
