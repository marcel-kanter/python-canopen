python-canopen
==============

|coverage|

.. |coverage| image:: https://img.shields.io/badge/coverage-100%25-green.svg
	:target: https://github.com/marcel-kanter/python-canopen

This package is a Python implementation of the CANopen standard, as defined in DS201, DS301 and DS1301.

It uses python-can as backend.

Features
--------

This package has the following capabilities and features:

- Communication to remote nodes on the can open bus
- Emulating of multiple local nodes in software

- `Mixed CAN/CANopen operation <docs/network/network.rst#mixed-cancanopen-operation>`_
- `Support for all data types defined by DS301 and DS1301 <docs/objectdictionary/variable.rst#data%20type>`_
