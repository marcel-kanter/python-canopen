Mixed CAN/CANopen operation sample
==================================

This example demonstrates the use of the package with an external notifier. The use of an external notifier is needed, if there are messages on the bus which are "pure" CAN messages and need separate processing.

Directly after opening the bus a message with the extended id 0x1000 is sent.

Then the CANopen ``Network`` object is created and attached to the bus.

To implement the notifier, a simple endless-loop is used. It passes all messages to the function process_message and afterwards to the message handler of Network.
Inside process_message all messages with extended ids are printed. Additionally if a message with the extened id of 0x2000 is received, the nmt state of node "somenode" (node id 1) is set to pre-operational.
