PDO
===

From the CANopen node's point of view, the node transmits TPDOs and receives RPDOs.

It is possible to configure a transmission type, which controls the sampling and transmit or the validation of the PDO data. Depending on the transmission type a SYNC message or an event is used as trigger for the transmission, sampling or validation.

TPDO
----

Allowed transmission types are:

* 0
* 1 ... 240
* 252
* 253
* 254
* 255

RPDO
----

Allowed transmission types are:

* 0
* 1 ... 240
* 254
* 255
