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
		with self.subTest("Init should leave the timer in a triggerable state and not start immediatly after init"):
			time.sleep(0.2)
			cb.assert_not_called()
			
			examinee.start(0.1)
			
			time.sleep(0.15)
			cb.assert_called()
		examinee.stop()
		del examinee
		del cb
		
		m = Mock()
		
		#### Test step: Invalid interval
		examinee = canopen.util.Timer(m, [10], {"a": 20})
		m.reset_mock()
		with self.subTest("Invalid interval"):
			
			with self.assertRaises(ValueError):
				examinee.start(-0.1)
		examinee.stop()
		del examinee
		
		#### Test step: Start with interval from init
		examinee = canopen.util.Timer(m, [10], {"a": 20})
		m.reset_mock()
		with self.subTest("Start with interval from init"):
			self.assertEqual(examinee.start(0.1), True)
			start_time = time.time()
			
			time.sleep(0.08 + start_time - time.time())
			m.assert_not_called()
			
			time.sleep(0.12 + start_time - time.time())
			m.assert_called()
						
			self.assertLess(time.time() - start_time, 0.15)
		examinee.stop()
		del examinee
		
		#### Test step: Cancel, start -> normal operation
		examinee = canopen.util.Timer(m, [10], {"a": 20})
		m.reset_mock()
		with self.subTest("Cancel, direct start -> normal operation"):
			examinee.cancel()
			self.assertEqual(examinee.start(0.1), True)
			start_time = time.time()
			
			time.sleep(0.08 + start_time - time.time())
			m.assert_not_called()
			
			time.sleep(0.12 + start_time - time.time())
			m.assert_called()
			
			self.assertLess(time.time() - start_time, 0.15)
		examinee.stop()
		del examinee
		
		examinee = canopen.util.Timer(m, [10], {"a": 20})
		m.reset_mock()
		with self.subTest("Cancel, sleep, start -> normal operation"):
			examinee.cancel()
			time.sleep(0.1)
			self.assertEqual(examinee.start(0.1), True)
			start_time = time.time()
			
			time.sleep(0.08 + start_time - time.time())
			m.assert_not_called()
			
			time.sleep(0.12 + start_time - time.time())
			m.assert_called()
			
			self.assertLess(time.time() - start_time, 0.15)
		examinee.stop()
		del examinee
		
		#### Test step: Start, cancel -> no call
		examinee = canopen.util.Timer(m, [10], {"a": 20})
		m.reset_mock()
		with self.subTest("Start, cancel -> no call"):
			examinee.start(0.1)
			start_time = time.time()
			
			examinee.cancel()
			
			time.sleep(0.2 + start_time - time.time())
			m.assert_not_called()
			
			self.assertLess(time.time() - start_time, 0.23)
		examinee.stop()
		del examinee
			
		examinee = canopen.util.Timer(m, [10], {"a": 20})
		m.reset_mock()
		with self.subTest("Start, delay, cancel -> no call"):
			examinee.start(0.1)
			start_time = time.time()
			
			time.sleep(0.08 + start_time - time.time())
			examinee.cancel()
			
			time.sleep(0.12 + start_time - time.time())
			m.assert_not_called()
			
			self.assertLess(time.time() - start_time, 0.15)
		examinee.stop()
		del examinee
		
		#### Test step: Start, start, cancel -> no call
		examinee = canopen.util.Timer(m, [10], {"a": 20})
		m.reset_mock()
		with self.subTest("Start, start, cancel -> no call"):
			self.assertEqual(examinee.start(0.1), True)
			self.assertEqual(examinee.start(0.1), True)
			start_time = time.time()
			
			time.sleep(0.03 + start_time - time.time())
			examinee.cancel()
			
			time.sleep(0.08 + start_time - time.time())
			m.assert_not_called()
			
			self.assertLess(time.time() - start_time, 0.13)
		examinee.stop()
		del examinee
		
		#### Test step: Start, cancel, start -> normal
		examinee = canopen.util.Timer(m, [10], {"a": 20})
		m.reset_mock()
		with self.subTest("Start, sleep, start, cancel -> no call"):
			self.assertEqual(examinee.start(0.1), True)
			start_time = time.time()
			
			time.sleep(0.03 + start_time - time.time())
			
			self.assertEqual(examinee.start(0.1), False)
			
			time.sleep(0.08 + start_time - time.time())
			examinee.cancel()
			
			time.sleep(0.12 + start_time - time.time())
			m.assert_not_called()
			
			self.assertLess(time.time() - start_time, 0.15)
		examinee.stop()
		del examinee
		
		examinee = canopen.util.Timer(m, [10], {"a": 20})
		m.reset_mock()
		with self.subTest("Start, cancel, start -> normal"):
			examinee.start(0.1)
			start_time = time.time()
			
			time.sleep(0.05 + start_time - time.time())
			examinee.cancel()
			
			time.sleep(0.15 + start_time - time.time())
			m.assert_not_called()
			
			examinee.start(0.1)
			start_time = time.time()
			
			time.sleep(0.08 + start_time - time.time())
			m.assert_not_called()
			
			time.sleep(0.12 + start_time - time.time())
			m.assert_called()
			
			self.assertLess(time.time() - start_time, 0.15)
		examinee.stop()
		del examinee
		
		examinee = canopen.util.Timer(m, [10], {"a": 20})
		m.reset_mock()
		with self.subTest("Start, cancel, start -> normal"):
			examinee.start(0.1)
			start_time = time.time()
			
			time.sleep(0.05 + start_time - time.time())
			examinee.cancel()
			
			m.assert_not_called()
			
			examinee.start(0.1)
			start_time = time.time()
			
			time.sleep(0.08 + start_time - time.time())
			m.assert_not_called()
			
			time.sleep(0.12 + start_time - time.time())
			m.assert_called()
			
			self.assertLess(time.time() - start_time, 0.15)
		examinee.stop()
		del examinee
		
		#### Test step: periodic mode
		examinee = canopen.util.Timer(m, [10], {"a": 20})
		m.reset_mock()
		with self.subTest("periodic mode"):
			examinee.start(0.1, True)
			start_time = time.time()
			
			time.sleep(0.05 + start_time - time.time())
			m.assert_not_called()
			
			time.sleep(0.15 + start_time - time.time())
			m.assert_called()
			m.reset_mock()
			
			time.sleep(0.25 + start_time - time.time())
			m.assert_called()
			m.reset_mock()
			
			time.sleep(0.35 + start_time - time.time())
			m.assert_called()
			m.reset_mock()
			
			examinee.cancel()
			time.sleep(0.45 + start_time - time.time())
			m.assert_not_called()
		examinee.stop()
		del examinee
		
		#### Test step: Stop, no call at the end
		examinee = canopen.util.Timer(m, [10], {"a": 20})
		m.reset_mock()
		with self.subTest("Stop, no call at the end"):
			examinee.start(0.2)
			start_time = time.time()
			
			time.sleep(0.1 + start_time - time.time())
			examinee.stop()
			
			time.sleep(0.3 + start_time - time.time())
			m.assert_not_called()
			
			self.assertFalse(examinee.is_alive())
			self.assertLess(time.time() - start_time, 0.35)
		del examinee
		
		del m
		
		#### Test step: Cancel inside callback
		m = Mock(side_effect = self.stoptimer_callback)
		self.examinee = canopen.util.Timer(m, [self])
		with self.subTest("Cancel inside callback"):
			self.counter = 0
			
			self.examinee.start(0.05, True)
			start_time = time.time()
			
			time.sleep(0.18 + start_time - time.time())
			self.assertEqual(self.counter, 3)
			
			# Callback should have incremented counter to 3 and canceled the timer - counter should not increment any more
			time.sleep(0.38 + start_time - time.time())
			self.assertEqual(self.counter, 3)
			
			# Start timer again
			self.counter = 0
			self.examinee.start(0.05, True)
			start_time = time.time()
			
			time.sleep(0.18 + start_time - time.time())
			self.assertEqual(self.counter, 3)
			
			# Callback should have incremented counter to 3 and canceled the timer - counter should not increment any more
			time.sleep(0.38 + start_time - time.time())
			self.assertEqual(self.counter, 3)
		self.examinee.stop()
		del self.examinee
		del m
	
	def stoptimer_callback(self, testcase):
		testcase.counter += 1
		if testcase.counter == 3:
			testcase.examinee.cancel()


if __name__ == "__main__":
	unittest.main()
