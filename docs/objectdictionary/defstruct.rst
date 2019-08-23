DefStruct
=========

This class is the representation of a DefStruct of an object dictionary. It is a mutable auto-associative mapping and may contain zero or more ``Variables``.
The Variable of subindex 0x00 must have the data type UNSIGNED8. This is the number of elements in the structure (the highest subindex supported and not counting subindex 0x00 and 0xFF).
All other variables (subindex 0x01 - 0xFE) must have the data type UNSIGNED8 or UNSIGNED16. They provide the datatype code.

Auto-associative mapping
------------------------

The ``DefStruct`` class is a mutable auto-associative mapping of Variables and the properties for association are subindex and name.
It's possible to get a ``Variable`` by subindex or name from the list.

To add a element to the mapping, the ``append`` function is used. The subindex and the name of the elements inside the mapping must be unique.
Additionally, the index of the variable must match the index of the record.

.. code:: python

	the_struct = canopen.objectdictionary.DefStruct("defstruct", 0x40)
	
	one_variable = canopen.objectdictionary.Variable("var1", 0x40, 0x01, canopen.objectdictionary.UNSIGNED8)
	other_variable = canopen.objectdictionary.Variable("var1", 0x40, 0x02, canopen.objectdictionary.UNSIGNED16)
	
	the_struct.append(one_variable)
	# This fails, because there is already a variable with name "var1".
	the_struct.append(other_variable)

After adding the element to the mapping, it can be accessed via subscription.
If the subindex and the name belong to the same element, the two lines will retrieve the same element:

.. code:: python

	# Use the subindex
	variable_1 = the_struct[0x01]
	# Use the name
	variable_1 = the_struct["var1"]
