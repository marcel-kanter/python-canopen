ObjectDictionary
================

This class is the representation of an object dictionary. It is a mutable auto-associative list and may contain zero or more Arrays, Records and Variables.

Auto-associative list
---------------------

The ``ObjectDictionary`` class is a mutable auto-associative list of Arrays, Records and Variables and the properties for association are index and name.
It's possible to get a Array, Record or Variable by index or name from the list.

To add a element to the network, the ``append`` function is used. The index and the name of the elements inside the object dictionary must be unique.

.. code:: python

	the_dictionary = canopen.ObjectDictionary()
	
	one_record = canopen.objectdictionary.Record("rec", 1)
	one_array = canopen.objectdictionary.Array("arr", 1)
	
	the_dictionary.append(one_record)
	# This fails, because there is already a record with index 1.
	the_dictionary.append(one_array)

After adding the element to the object dictionary, it can be accessed trough the object dictionary via subscription.
If the index and the name belong to the same element, the two lines will retrieve the same element:

.. code:: python

	# Use the index
	record_1 = the_dictionary[1]
	# Use the name
	record_1 = the_dictionary["rec"]
