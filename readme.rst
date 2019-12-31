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
- `Support for all data types defined by DS301 and DS1301 <docs/objectdictionary/variable.rst#data-type>`_

Protocol support

+------------------+----------------+------------------------------------+
| CANopen Protocol | State          | Comments                           |
+------------------+----------------+------------------------------------+
| EMCY Consumer    | Testing        |                                    |
+------------------+----------------+------------------------------------+
| EMCY Producer    | Testing        |                                    |
+------------------+----------------+------------------------------------+
| LSS Slave        | Analysis       |                                    |
+------------------+----------------+------------------------------------+
| LSS Slave        | Analysis       |                                    |
+------------------+----------------+------------------------------------+
| NMT Master       | Analysis       |                                    |
+------------------+----------------+------------------------------------+
| NMT Slave        | Testing        | Use NMTMaster for remote nodes     |
+------------------+----------------+------------------------------------+
| PDO Consumer     | Implementation |                                    |
+------------------+----------------+------------------------------------+
| PDO Producer     | Implementation |                                    |
+------------------+----------------+------------------------------------+
| SDO Consumer     | Testing        |                                    |
+------------------+----------------+------------------------------------+
| SDO Producer     | Testing        |                                    |
+------------------+----------------+------------------------------------+
| SRDO Consumer    | Analysis       |                                    |
+------------------+----------------+------------------------------------+
| SRDO Producer    | Analysis       |                                    |
+------------------+----------------+------------------------------------+
| SYNC Consumer    | Testing        |                                    |
+------------------+----------------+------------------------------------+
| SYNC Producer    | Testing        |                                    |
+------------------+----------------+------------------------------------+
| TIME Consumer    | Testing        |                                    |
+------------------+----------------+------------------------------------+
| TIME Producer    | Testing        |                                    |
+------------------+----------------+------------------------------------+
