Timer
=====

The canopen package provides a timer utility class for managing time-dependend functionality like timeouts or sending messages periodically.

Creating the timer instance does not trigger to timer. Thus it is possbile to create the needed timers at program start (which involves creating threads and takes some time) and later use it when needed.
The timer can be used in one-shot or periodic mode and is reusable. Reusable means that the time interval can be started again without recreation of the timer. It is also possible to mix the operational modes.
After one-shot mode, the same timer can be used in periodic mode and vise-versa.
Additionally the ``Timer`` class provides a ``cancel`` function which resets the timer into the waiting state.
For a proper clean-up the ``stop`` function should be called. Elsewise the timer may call the callback and the main thread is already exiting.
Raising an exception in the callback will leave the timer in an unusable state.

One-shot mode
-------------

In one-shot mode, the time from start to the invocation of the callback is set individually.

.. code::

	+-------------+--------+-------+----+-----+-> time
	S             E        S       E    S     E
	T             V        T       V    T     V
	A             E        A       E    A     E
	R             N        R       N    R     N
	T             T        T       T    T     T

Calling the ``cancel`` function will stop the timer cycle and block until the timer is ready to be triggered (started) again.

.. code::

	+------+------X--------+-------+----+-----+-> time
	S      C               S       E    S     E
	T      A               T       V    T     V
	A      N               A       E    A     E
	R      C               R       N    R     N
	T      E               T       T    T     T
	       L


Periodic mode
-------------

In periodic mode, the interval between each invocation of the callback is set at start. The time until the next invocation of the callback is calculated after each event, keeping the average interval correct. This minimizes the influence of the runtime of the callback. 

.. code::

	+-----+------+----+-----+------+----+-----+-> time
	S     E      E    E     E      E    E     E 
	T     V      V    V     V      V    V     V 
	A     E      E    E     E      E    E     E 
	R     N      N    N     N      N    N     N 
	T     T      T    T     T      T    T     T 

Calling the ``cancel`` function will stop the timer cycle and block until the timer is ready to be triggered (started) again.

.. code::

	+-----+------+----+-----+--+---X-+--+--+--+-> time
	S     E      E    E     E  C     S  E  E  E 
	T     V      V    V     V  A     T  V  V  V 
	A     E      E    E     E  N     A  E  E  E 
	R     N      N    N     N  C     R  N  N  N 
	T     T      T    T     T  E     T  T  T  T 
	                           L
