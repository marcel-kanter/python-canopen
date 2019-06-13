CANopenSpy
==========

Step 1
------

The basic program sequence is:

1. Create the can bus and the canopen network.
2. Attach the network to the bus.
3. Do something with the bus and/or the network.
4. Detach the netowrk from the bus.
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

Step 2
------

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

Step 3
------

Spy service for NMT.

Each ``Node`` has services with care about the can messages. Create a service for the NMT related messages.
The services are usually created at creation of the node, attached to the node, when the node is attached to the network and detached when the node is detached from the network.

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

Step 4
------

Let NMTSpy print the NMT messages.

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
		
		def on_error_control(self, message):
			print(message)

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
