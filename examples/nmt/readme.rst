NMT Sample
==========

These examples show the usage of the NMT service and the error control functionality.

localnode-heartbeat.py
----------------------

It takes the heartbeat time as argument. 

The example code creates a local node and starts the periodical sending of the heartbeat messages. First the boot-up message is send, then for one second the node stays in pre operational state. After this second, the state is changed to operational.

The content of the heartbeat message reflects the NMT state of the local node after changing the state property of the NMT service.

remotenode-guarding.py
----------------------

It takes the guarding time and the life time factor as argument.

The example code creates a remote node, sends and node control request the change the state of the node to pre operational and then starts guarding the node. If an guarding event occurs, "guarding event" is print.
