Network
=======

This class is the representation of a CANopen network. It is a mutable auto-associative mapping and may contain zero or more CANopen nodes.

To use Network together with a CAN bus, first the CAN bus instance must be created and then the network attached to the bus.
In the end, the network must be detached from the CAN bus.

Attach/detach
-------------

The attach/detach pattern is used create a link from the ``Network`` (child) to the ``Bus`` (parent). It only creates a functional relationship between them.

The structural relation between the child and the parent must be handled by other means (the ``Bus`` class has no functionality for this).

.. code:: python

	# First create a bus
	bus = can.Bus(interface = "virtual", channel = 0)
	
	# It's possible to use the can bus now, as described in the python-can documentation.
	# You may send and receive messages, etc.
	
	# Create the canopen Network instance and attach it to the bus
	network = canopen.Network()
	network.attach(bus)
	
	# Using bus.send() works as expected between Network.attach() and Notwork.detach().
	# Using bus.recv() does not work or it disturbs the proper operation of the Network.
	# See the chapter Mixed CAN/CANopen operation.
	
	# Detach the canopen Network before shutdown of the can bus.
	network.detach()
	
	# The can bus is still open and usable at this point.
	
	# Clean up
	bus.shutdown()

Mixed CAN/CANopen operation
---------------------------

The CANopen standards do not prohibit the use of CAN messages together with messages that belong to the CANopen protocol. The ``Network`` class provides the possibility to be operated in a mixed CAN/CANopen environment.

If such operation is needed an external message notifier must be implemented and all (relevant) CAN messages must be passed to ``Network.on_message``. This can be achieved by overloading ``can.Notifier`` or by a simple endless loop.
When attaching to the bus, the ``builtin_notifier`` must be set to ``False``.

.. code:: python
	
	# Create the canopen Network instance and attach it to the bus
	network = canopen.Network()
	network.attach(bus, False)
	
	# Simple endless-loop "notifier". This is a stripped version of the internal code of ``can.Notifier``
	_finish = False
	msg = None
	while not _finish:
		if msg is not None:
			# check if msg is a CAN message and process it
			# process_message(msg)
			
			# pass the msg to the message handler of network
			network.on_message(msg)
			
		# Receive new message, if any
		msg = bus.recv(1.0)
		
	# Detach the canopen Network before shutdown of the can bus.
	network.detach()

Auto-associative mapping
------------------------

The ``Network`` class is a mutable auto-associative mapping of nodes and the properties for association are id and name.
It's possible to get a node by id or name from the mapping.

To add a node to the mapping, the ``add`` function is used. The id and the name of the nodes inside the mapping must be unique.

.. code:: python

	the_network = canopen.Network()
	
	one_node = canopen.Node("A", 1, dictionary)
	other_node = canopen.Node("B", 1, dictionary)
	
	the_network.add(one_node)
	# This fails, because there is already a node with id 1 in the_network.
	the_network.add(other_node)

After adding the node to the list, it can be accessed via subscription.
If the id and the name belong to the same node, the two lines will retrieve the same node:

.. code:: python

	# Use the id
	node_1 = the_network[1]
	# Use the name
	node_A = the_network["A"]

It implements the iterator interface too. The iterator yields all nodes added to the ``Network``.

.. code:: python

	the_network = canopen.Network()
	
	# ... add some nodes ...
	
	for n in the_network:
		print(n.name)
