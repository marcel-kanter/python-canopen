import sys
import os
import time
import numpy

if __name__ == "__main__":
	# Let import look in the CWD too
	sys.path.append(os.getcwd())

from canopen.util import Timer

tt = []

st = 0

def fkt():
	global tt
	tt.append(('FKT', time.time()))

def sle():
	global tt
	global st
	tt.append(('FKT', time.time()))
	if st == 0:
		time.sleep(0.6)
		st += 1
	else:
		time.sleep(0.2) 

if __name__ == '__main__':
	print("Test of periodic mode with callback that needs more time than interval")
	t = Timer(sle)
	tt.append(('INIT', time.time()))
	t.start(0.5, True)
	tt.append(('START', time.time()))
	time.sleep(1.8)
	tt.append(('STOP', time.time()))
	t.stop()
	
	t_start = 0
	for x in tt:
		print(x)
		if x[0] == 'START':
			t_start = x[1]
		if x[0] == 'CANCEL' and t_start != 0:
			print("\tdelta=" + str(x[1] - t_start))
		if x[0] == 'STOP' and t_start != 0:
			print("\tdelta=" + str(x[1] - t_start))
		if x[0] == 'FKT':
			print("\tdelta=" + str(x[1] - t_start))
			t_start = x[1]
	
	print("There should be 3 calls to the function. The second one a bit off-time since the first run of the callback needs more time.")
	print("First delta = 0.5, second delta = 0.6 (the callback takes 0.6s), third delta = 0.4 (to stay in the 0.5s interval).")
	
	print("")
	print("Timer class Performance measurement")
	print("Step 1: Function calls")
	tt = []
	t = Timer(fkt)
	tt.append(('INIT', time.time()))
	time.sleep(0.1)
	t.start(0.5)
	tt.append(('START', time.time()))
	time.sleep(0.3)
	t.cancel()
	tt.append(('CANCEL', time.time()))
	t.start(0.5)
	tt.append(('START', time.time()))
	time.sleep(0.7)
	t.cancel()
	tt.append(('CANCEL', time.time()))
	t.start(0.5)
	tt.append(('START', time.time()))
	time.sleep(0.7)
	t.start(0.5)
	tt.append(('START', time.time()))
	time.sleep(0.3)
	t.stop()
	tt.append(('STOP', time.time()))
	time.sleep(0.7)
	
	t_start = 0
	for x in tt:
		print(x)
		if x[0] == 'START':
			t_start = x[1]
		if x[0] == 'CANCEL' and t_start != 0:
			print("\tdelta=" + str(x[1] - t_start))
		if x[0] == 'STOP' and t_start != 0:
			print("\tdelta=" + str(x[1] - t_start))
		if x[0] == 'FKT':
			print("\tdelta=" + str(x[1] - t_start))
	
	print("")
	print("Start to cancel: " + str(tt[2][1] - tt[1][1]) + " should be 0.3")
	print("Start to function: " + str(tt[4][1] - tt[3][1]) + " should be 0.5")
	print("Start to function: " + str(tt[7][1] - tt[6][1]) + " should be 0.5")
	
	print("")
	print("Step 2: Timing jitter, one shot mode")
	tt = []
	n = 0
	jitter_timer = Timer(fkt)
	for n in range(50):
		jitter_timer.start(0.4)
		tt.append(('START', time.time()))
		time.sleep(0.5)
	
	jitter_timer.stop()
	
	tc = []
	t_start = 0
	for x in tt:
		print(x)
		if x[0] == 'START':
			t_start = x[1]
		if x[0] == 'CANCEL' and t_start != 0:
			print("\tdelta=" + str(x[1] - t_start))
		if x[0] == 'STOP' and t_start != 0:
			print("\tdelta=" + str(x[1] - t_start))
		if x[0] == 'FKT':
			print("\tdelta=" + str(x[1] - t_start))
			tc.append(x[1] - t_start)
	
	print("")
	print("min: " + str(numpy.min(tc)))
	print("mean: " + str(numpy.mean(tc)))
	print("stddev: " + str(numpy.std(tc)))
	print("max: " + str(numpy.max(tc)))
	
	print("")
	print("Step 3: Timing jitter, periodic mode")
	tt = []
	n = 0
	jitter_timer = Timer(fkt)
	jitter_timer.start(0.4, True)
	tt.append(('START', time.time()))
	time.sleep(25)
	jitter_timer.stop()
	
	tc = []
	t_start = 0
	for x in tt:
		print(x)
		if x[0] == 'START':
			t_start = x[1]
		if x[0] == 'CANCEL' and t_start != 0:
			print("\tdelta=" + str(x[1] - t_start))
		if x[0] == 'STOP' and t_start != 0:
			print("\tdelta=" + str(x[1] - t_start))
		if x[0] == 'FKT':
			print("\tdelta=" + str(x[1] - t_start))
			tc.append(x[1] - t_start)
			t_start = x[1]
	
	print("")
	print("min: " + str(numpy.min(tc)))
	print("mean: " + str(numpy.mean(tc)))
	print("stddev: " + str(numpy.std(tc)))
	print("max: " + str(numpy.max(tc)))
