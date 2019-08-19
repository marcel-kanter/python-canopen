CANopenSpy
==========

1. Subclassing a Node
---------------------

This chapter shows some basic steps on how to subclass the Node class and equipping it with a custom service.

Step 1. Main program
~~~~~~~~~~~~~~~~~~~~

The basic program sequence is:

1. Create the can bus and the canopen network.
2. Attach the network to the bus.
3. Do something with the bus and/or the network.
4. Detach the network from the bus.
5. Close the can bus.

spy.py

.. code:: python 

	import can
	import canopen
	
	if __name__ == "__main__":
		bus = can.Bus(interface = "ixxat", channel = 0, bitrate = 100000)
		network = canopen.Network()
		network.attach(bus)
	
		network.detach()
		bus.shutdown()

Step 2. Package with custom class
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create package canopenspy with a class SpyNode.

The ``SpyNode`` will be a sub-class of ``Node`` and does all the work. After creation it needs to attached to the network and in the end detached. 

canopenspy/node/spynode.py

.. code:: python

	import canopen
	
	class SpyNode(canopen.Node):
		def __init__(self, name, node_id):
			canopen.Node.__init__(self, name, node_id, canopen.ObjectDictionary())

canopenspy/node/__init__.py

.. code:: python

	from .spynode import SpyNode

canopenspy/__init__.py

.. code:: python

	from .node import SpyNode

spy.py

.. code:: python

	import can
	import canopen
	from canopenspy import SpyNode
	
	if __name__ == "__main__":
		bus = can.Bus(interface = "ixxat", channel = 0, bitrate = 100000)
		network = canopen.Network()
		spy = SpyNode("1", 1)
		
		network.attach(bus)
		spy.attach(network)
		
		spy.detach()
		network.detach()
		bus.shutdown()

Step 3. Spy service for NMT protocol
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each ``Node`` has services which care about the can messages. Create a service for the NMT related messages.
The services are usually created at creation of the node. They get attached to the node when the node is attached to the network and detached when the node is detached from the network.

canopenspy/node/service/nmt/nmtspy.py

.. code:: python

	import canopen.node.service
	
	class NMTSpy(canopen.node.service.Service):
		pass

canopenspy/node/service/nmt/__init__.py

.. code:: python

	from .nmtspy import NMTSpy

canopenspy/node/service/__init__.py

.. code:: python

	from .nmt import NMTSpy

canopenspy/node/spynode.py

.. code:: python

	import canopen
	from .service import NMTSpy
	
	class SpyNode(canopen.Node):
		def __init__(self, name, node_id):
			canopen.Node.__init__(self, name, node_id, canopen.ObjectDictionary())
			self.nmt = NMTSpy()
		
		def attach(self, network):
			canopen.Node.attach(self, network)
			self.nmt.attach(self)
		
		def detach(self):
			self.nmt.detach()
			canopen.Node.detach(self)

Step 4. Let NMTSpy print the messages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To get the messages with a specific message id, use the subscribe function of the ``Network`` class.
When a message on the can bus with the message id is recieved, the callback function is called.
Callbacks need to short and non-blocking, or else they will introduce latency or block the program flow.

canopenspy/node/service/nmt/nmtspy.py

.. code:: python

	from canopen.node.service import Service
	
	class NMTSpy(Service):
		def __init__(self):
			Service.__init__(self)
		
		def attach(self, node):
			Service.attach(self, node)
			self._node.network.subscribe(self.on_node_control, 0x000)
			self._node.network.subscribe(self.on_error_control, 0x700 + self._node.id)
		
		def detach(self):
			self._node.network.unsubscribe(self.on_error_control, 0x700 + self._node.id)
			self._node.network.unsubscribe(self.on_node_control, 0x000)
			Service.detach(self)
		
		def on_node_control(self, message):
			print(message)
			print("NMT: node control")
		
		def on_error_control(self, message):
			print(message)
			print("NMT: error control")

spy.py

.. code:: python

	import time
	import can
	import canopen
	from canopenspy import SpyNode
	
	if __name__ == "__main__":
		bus = can.Bus(interface = "ixxat", channel = 0, bitrate = 10000)
		network = canopen.Network()
		spy = SpyNode("1", 1)
		
		network.attach(bus)
		spy.attach(network)
		
		print("press CTRL-C to quit")
		try:
			while True:
				time.sleep(1)
		except:
			pass
		
		spy.detach()
		network.detach()
		bus.shutdown()

Test
~~~~

The program will show NMT messages, when it receives them:

.. code:: console

	press CTRL-C to quit
	Timestamp:     1187.566894        ID: 0000    S                DLC:  8    40 01 10 00 00 00 00 00     Channel: 0
	NMT: node control
	Timestamp:     1195.062588        ID: 0000    S                DLC:  8    40 01 10 00 00 00 00 00     Channel: 0
	NMT: node control
	Timestamp:     1195.926682        ID: 0000    S                DLC:  8    40 01 10 00 00 00 00 00     Channel: 0
	NMT: node control
	Timestamp:     1207.648163        ID: 0701    S                DLC:  1    01                          Channel: 0
	NMT: error control
	Timestamp:     1214.039344        ID: 0701    S   R            DLC:  1                                Channel: 0
	NMT: error control

2. Subclassing a Service
------------------------

Step 1. SYNCSpy
~~~~~~~~~~~~~~~

canopenspy/node/service/sync/syncspy.py

.. code:: python

	from canopen.node.service.sync import SYNCConsumer

	class SYNCSpy(SYNCConsumer):
		def on_sync(self, message):
			print(message)
			SYNCConsumer.on_sync(self, message)

canopenspy/node/service/sync/__init__.py

.. code:: python

	from .syncspy import SYNCSpy

canopenspy/node/service/__init__.py

.. code:: python

	from .nmt import NMTSpy
	from .sync import SYNCSpy

Step 2. Use SYNCSpy in SpyNode
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use the SYNCSpy in the SpyNode. Add a callback for printing information about the SYNC message.

canopenspy/node/spynode.py

.. code:: python

	import canopen
	from .service import NMTSpy, SYNCSpy
	
	class SpyNode(canopen.Node):
		def __init__(self, name, node_id):
			canopen.Node.__init__(self, name, node_id, canopen.ObjectDictionary())
			self.nmt = NMTSpy()
			self.sync = SYNCSpy()
			self.sync.add_callback("sync", self.sync_callback)
		
		def attach(self, network):
			canopen.Node.attach(self, network)
			self.nmt.attach(self)
			self.sync.attach(self)
		
		def detach(self):
			self.sync.detach()
			self.nmt.detach()
			canopen.Node.detach(self)
		
		def sync_callback(self, event, node, counter):
			if counter == None:
				print("SYNC: no counter")
			else:
				print("SYNC: counter=" + str(counter))

Test
~~~~

The program will show SYNC messages and in the callback, the counter value is evaluated. Note that RTR messages are filtered by SYNCConsumer and thus the callback is not called for them.

.. code:: console

	press CTRL-C to quit
	Timestamp:     1475.863103        ID: 0080    S                DLC:  1    00                          Channel: 0
	SYNC: counter=0
	Timestamp:     1477.815169        ID: 0080    S                DLC:  1    01                          Channel: 0
	SYNC: counter=1
	Timestamp:     1479.119166        ID: 0080    S                DLC:  1    01                          Channel: 0
	SYNC: counter=1
	Timestamp:     1482.966143        ID: 0080    S   R            DLC:  1                                Channel: 0
	Timestamp:     1487.255078        ID: 0080    S                DLC:  1    01                          Channel: 0
	SYNC: counter=1
