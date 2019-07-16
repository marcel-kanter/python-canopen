Node
====

This class is the base class for CANopen nodes. It is an immutable auto-associative list and may contain zero or more variables, records or arrays.
The structure of the objects is defined with an object dictionary. Since the object dictionary only describes the structure, it can be used for multiple nodes.

The functions for data access are not implemented.

Access to objects
-----------------

The objects of a node can be accessed by subscription.

.. code:: python

	the_node = canopen.Node("A", 1, dictionary)
	device_type_index = the_node["Device type"].index
