LocalNode
=========

This class is a representation of a local CANopen node. It is an immutable auto-associative list and may contain zero or more variables, records or arrays.
The structure of the objects is defined with an object dictionary. Since the object dictionary only describes the structure, it can be used for multiple nodes.

The data of each object is held by the node itself. To access the data via can bus SDO transfers can be used.

The following services are used by this class:

* NMT client
* EMCY producer
* SDO server

Access to objects
-----------------

The objects of a node can be accessed by subscription.

.. code:: python

	the_node = canopen.LocalNode("A", 1, dictionary)
	device_type = the_node["Device type"].value