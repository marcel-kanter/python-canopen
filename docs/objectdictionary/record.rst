Record
======

This class is the representation of a record of an object dictionary. It is a mutable auto-associative mapping and may contain zero or more of ``Variable``.

Auto-associative mapping
------------------------

The ``Record`` class is a mutable auto-associative mapping of Variables and the properties for association are subindex and name.
It's possible to get a ``Variable`` by subindex or name from the mapping.

To add a element to the mapping, the ``add`` function is used. The subindex and the name of the elements inside the mapping must be unique.
Additionally, the index of the variable must match the index of the record.

.. code:: python

	the_record = canopen.objectdictionary.Record("rec", 0x1000)
	
	one_variable = canopen.objectdictionary.Variable("var1", 0x1000, 0x01, canopen.objectdictionary.INTEGER32)
	other_variable = canopen.objectdictionary.Variable("var2", 0x1000, 0x01, canopen.objectdictionary.INTEGER32)
	
	the_record.add(one_variable)
	# This fails, because there is already a variable with subindex 1.
	the_record.add(other_variable)

After adding the element to the list, it can be accessed via subscription.
If the subindex and the name belong to the same element, the two lines will retrieve the same element:

.. code:: python

	# Use the subindex
	variable_1 = the_record[0x01]
	# Use the name
	variable_1 = the_record["var1"]

It implements the iterator interface too. The iterator yields all elements (variables, ...) added to the ``Record``.

.. code:: python

	the_record = canopen.objectdictionary.Record("rec", 0x1000)
	
	# ... add some elements ...
	
	for v in the_record:
		print(v.name)
