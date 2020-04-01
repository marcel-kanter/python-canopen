RemoteNode
=========

This class is a representation of a remote CANopen node. It is an immutable auto-associative mapping and may contain zero or more variables, records or arrays.
The structure of the objects is defined with an object dictionary. Since the object dictionary only describes the structure, it can be used for multiple nodes.

No data of any object is held by the node. For every access to an object's value a SDO transfer is used.

The following services are used by this class:

* Remote NMT slave
* EMCY client
* SDO client

Attach/detach
-------------

The attach/detach pattern is used create a link from the ``RemoteNode`` (child) to the ``Network`` (parent). It only creates a functional relationship between them.
The structural relation between the child and the parent is handled by other means.

Access to objects
-----------------

The objects of a node can be accessed by subscription, if the object exists in the object dictionary. This will start a SDO transfer to get/set the acutal data.

.. code:: python

	the_node = canopen.RemoteNode("A", 1, dictionary)
	device_type = the_node["Device type"].value
