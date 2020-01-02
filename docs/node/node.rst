Node
====

This class is the base class for CANopen nodes. It is an immutable auto-associative mapping and may contain zero or more variables, records or arrays.
The structure of the objects is defined with an object dictionary. Since the object dictionary only describes the structure, it can be used for multiple nodes.

The functions for data access are not implemented.

The identifier of the node can have a value of 1 to 127 or 255. If the node is not attached to a network, the identifier can be changed. The node cannot be attached if the identifier is 255.

Attach/detach
-------------

The attach/detach pattern is used create a link from the ``Node`` (child) to the ``Network`` (parent). It only creates a functional relationship between them.
The structural relation between the child and the parent is handled by other means.

Access to objects
-----------------

The objects of a node can be accessed by subscription.

.. code:: python

	the_node = canopen.Node("A", 1, dictionary)
	device_type_index = the_node["Device type"].index
