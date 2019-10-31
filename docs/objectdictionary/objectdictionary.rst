ObjectDictionary
================

This class is the representation of an object dictionary. It is a mutable auto-associative mapping and may contain zero or more of ``Array``, ``DefStruct``, ``DefType``, ``Domain``, ``Record`` and ``Variable``.

+-----------+-------------+
| Class     | Object Type |
+===========+=============+
| Array     | 8           |
+-----------+-------------+
| DefStruct | 6           |
+-----------+-------------+
| DefType   | 5           |
+-----------+-------------+
| Domain    | 2           |
+-----------+-------------+
| Record    | 9           |
+-----------+-------------+
| Variable  | 7           |
+-----------+-------------+

Auto-associative mapping
------------------------

The ``ObjectDictionary`` class is a mutable auto-associative mapping of Arrays, Records and Variables and the properties for association are index and name.
It's possible to get a ``Array``, ``DefStruct``, ``DefType``, ``Domain``, ``Record`` or ``Variable`` by index or name from the mapping.

To add a element to the mapping, the ``add`` function is used. The index and the name of the elements inside the mapping must be unique.

.. code:: python

	the_dictionary = canopen.ObjectDictionary()
	
	one_record = canopen.objectdictionary.Record("rec", 1)
	one_array = canopen.objectdictionary.Array("arr", 1)
	
	the_dictionary.add(one_record)
	# This fails, because there is already an object with index 1 in the object dictionary.
	the_dictionary.add(one_array)

After adding the element to the list, it can be accessed via subscription.
If the index and the name belong to the same element, the two lines will retrieve the same element:

.. code:: python

	# Use the index
	record_1 = the_dictionary[1]
	# Use the name
	record_rec = the_dictionary["rec"]

It implements the iterator interface too. The iterator yields all elements (arrays, records, variables, ...) added to the dictionary.

.. code:: python

	the_dictionary = canopen.ObjectDictionary()
	
	# ... add some elements ...
	
	for o in the_dictionary:
		print(o.name)
