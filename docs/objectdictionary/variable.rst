Variable
========

This class is the representation of an variable of an object dictionary.
It describes only the object in the dictionary and does not hold any actual data of a node.

The properties of the ``Variable`` are immutable and cannot be changed after creation of the variable.

Each variable has a data type. The data types are defined in DS301 and the following data types are supported.

* BOOLEAN
* INTEGER8
* INTEGER16
* INTEGER32
* UNSIGNED8
* UNSIGNED16
* UNSIGNED32
* REAL32
* VISIBLE_STRING
* OCTET_STRING
* UNICODE_STRING
* TIME_OF_DAY
* TIME_DIFFERENCE
* DOMAIN
* INTEGER24
* REAL64
* INTEGER40
* INTEGER48
* INTEGER56
* INTEGER64
* UNSIGNED24
* UNSIGNED40
* UNSIGNED48
* UNSIGNED56
* UNSIGNED64

Each variable has an access type. The access types as defined in DS301 and the follwing access types are supported.

* rw
* wo
* ro

Encode/Decode
-------------

For conversion of python variables into the CANopen representation and back, the functions ``encode`` and ``decode`` are used.

.. code:: python

	one_variable = canopen.objectdictionary.Variable("var1", 0x1000, 0x01, canopen.objectdictionary.INTEGER32)
	# Convert the constant 1234 into bytes containing CANopen representation
	encoded = one_variable.encode(1234)
	# Convert the encoded bytes into python variable
	decoded = one_variable.decode(b"\xAA\x00\x00\x00")
	
	one_variable = canopen.objectdictionary.Variable("var1", 0x1000, 0x01, canopen.objectdictionary.VISIBLE_STRING)
	# Convert python string with ascii encoding into bytes containing CANopen representation
	# This may raise an exception, if the text includes non-ascii characters
	encoded = one_variable.encode("TestText")

TIME_OF_DAY
~~~~~~~~~~~

A variable of type TIME_OF_DAY represents a time in the CANOpen epoch, which starts at 1st January 1984 00:00:00. The resolution is 1 ms.
Negative times are not allowed.

TIME_DIFFERENCE
~~~~~~~~~~~~~~~

A variable of type TIME_DIFFERENCE represents a time span. The resolution is 1 ms.
Negative time differences are not allowed.
