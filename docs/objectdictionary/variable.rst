Variable
========

This class is the representation of an variable of an object dictionary.
It describes only the object in the dictionary and does not hold any actual data of a node.

The most properties of the ``Variable`` are immutable and cannot be changed after creation of the variable.
Only access_type and default can be changed after creation.

Each variable has a data type. The data types are defined in DS301 "Table 44: Object dictionary data types" and the following data types are supported.

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

Each variable has an access type. The access types as defined in DS301 "Table 43: Access attributes for data objects" and the follwing access types are supported.

* rw
* wo
* ro

A ``Variable`` has a default value. Depending on the data type, the default value is set to False, 0 or empty data at creation of the Variable object. It can be changed if needed.

Encode/Decode
-------------

For conversion of python variables into the CANopen representation and back, the functions ``encode`` and ``decode`` are used. The usage of both functions are similar to the ones of python's built-in objects.

.. code:: python

	one_variable = canopen.objectdictionary.Variable("var1", 0x1000, 0x01, canopen.objectdictionary.INTEGER32)
	# Convert the constant 1234 into bytes containing CANopen representation
	encoded = one_variable.encode(1234)
	# Convert the encoded bytes into python variable
	decoded = one_variable.decode(b"\xAA\x00\x00\x00")
	
	one_variable = canopen.objectdictionary.Variable("var1", 0x1000, 0x01, canopen.objectdictionary.VISIBLE_STRING)
	# Convert python string into bytes containing CANopen representation using ASCII encoding
	# This may raise an exception, if the text includes non-ascii characters
	encoded = one_variable.encode("TestText")
	
	one_variable = canopen.objectdictionary.Variable("var1", 0x1000, 0x01, canopen.objectdictionary.UNICODE_STRING)
	# Convert python string into bytes containing CANopen representation using UTF-16-LE encoding
	# This may raise an exception, if the text includes characters which cannot be encoded with utf-16
	encoded = one_variable.encode("TestText")

VISIBLE_STRING
~~~~~~~~~~~~~~

DS201 defines ASCII as character set. But only the values 0 and 0x20 to 0x7E are admissible.
DS301 and DS1301 defines ISO646:1973 as character set. But only the values 0 and 0x20 to 0x7E are admissible.

However this library uses the built-in ascii character set of python and thus may encode bytes that are not inside the range of admissible values.

OCTET_STRING
~~~~~~~~~~~~

DS201, DS301 and DS1301 don't define a character set. The width of each encoded character shall be 8 bits. 

This library uses UTF-8 encoding, as this matches the 8 bits requirement and all unicode code points can be encoded.

UNICODE_STRING
~~~~~~~~~~~~~~

DS201 does not define this data type.
DS301 only defines the length of each encoded character to be 16 bits.
DS1301 defines ISO10646:2003 UCS-2 as character set, which is only 16 bit wide.

However since UCS-2 is obsolete now, this library uses utf-16-le as encoding, as this is the most comparable.

TIME_OF_DAY
~~~~~~~~~~~

A variable of type TIME_OF_DAY represents a time in the CANOpen epoch, which starts at 1st January 1984 00:00:00. The resolution is 1 ms.
Negative times are not allowed.

TIME_DIFFERENCE
~~~~~~~~~~~~~~~

A variable of type TIME_DIFFERENCE represents a time span. The resolution is 1 ms.
Negative time differences are not allowed.
