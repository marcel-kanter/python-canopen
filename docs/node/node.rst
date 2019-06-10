Node
====

This class is a basic representation of a CANopen node. It is an immutable auto-associative list and may contain zero or more variables, records or arrays.
The structure of the objects is defined with an object dictionary. Since the object dictionary only describes the structure, it can be used for multiple nodes.
The data of each object is held by the node itself.

Access to objects
-----------------

The objects of a node can be accessed by subscription.

.. code:: python

	the_node = canopen.Node("A", 1, dictionary)
	device_type_index = the_node["Device type"].index
