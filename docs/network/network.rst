Network
=======

This class is the representation of a CANopen network. It is a mutable auto-associative mapping and may contain zero or more CANopen nodes.

To use Network together with a CAN bus, first the CAN bus instance must be created and then the network attached to the bus.
In the end, the network must be detached from the CAN bus.

Attach/detach
-------------

The attach/detach pattern is used create a link from the ``Network`` (child) to the ``Bus`` (parent). It only creates a functional relationship between them.
The structural relation between the child and the parent is handled by other means.

.. code:: python

	# First create a bus
	bus = can.Bus(interface = "virtual", channel = 0)
	# It's possible to use the can bus now, as described in the python-can documentation. You may send and receive messages, etc.
	
	# Create the canopen Network instance and attach it to the bus
	network = canopen.Network()
	network.attach(bus)
	
	# Detach the canopen Network before shutdown of the can bus.
	network.detach()
	
	# Clean up
	bus.shutdown()

Auto-associative mapping
------------------------

The ``Network`` class is a mutable auto-associative mapping of nodes and the properties for association are id and name.
It's possible to get a node by id or name from the mapping.

To add a node to the mapping, the ``append`` function is used. The id and the name of the nodes inside the mapping must be unique.

.. code:: python

	the_network = canopen.Network()
	
	one_node = canopen.Node("A", 1, dictionary)
	other_node = canopen.Node("B", 1, dictionary)
	
	the_network.append(one_node)
	# This fails, because there is already a node with id 1.
	the_network.append(other_node)

After adding the node to the list, it can be accessed via subscription.
If the id and the name belong to the same node, the two lines will retrieve the same node:

.. code:: python

	# Use the id
	node_1 = the_network[1]
	# Use the name
	node_A = the_network["A"]
