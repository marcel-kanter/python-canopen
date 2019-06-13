CANopenSpy
==========

Step 1
------

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
