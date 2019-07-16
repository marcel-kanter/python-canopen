RemoteNode
=========

This class is a representation of a remote CANopen node. It is an immutable auto-associative list and may contain zero or more variables, records or arrays.
The structure of the objects is defined with an object dictionary. Since the object dictionary only describes the structure, it can be used for multiple nodes.

No data of any object is held by the node. For every access to an object's value a SDO transfer is used.

The following services are used by this class:

* NMT master
* EMCY client
* SDO client

Access to objects
-----------------

The objects of a node can be accessed by subscription.

.. code:: python

	the_node = canopen.RemoteNode("A", 1, dictionary)
	device_type = the_node["Device type"].value
