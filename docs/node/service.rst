Service
=======

The ``Service`` class is the base class for all services of a ``Node``.

Attach/detach
-------------

The attach/detach methods are used as handlers of the the attach/detach of the node the service belongs to. The attach/detach method normally is called from the attach/detach method of the node to set up the service correctly.

Callbacks
---------

Callbacks are used to inform the application about events. After the application has added its callback function(s) to the service, they get called when an event occured.
The first argument for th callback is the event name, the rest of the arguments depend on the implementation of the sub-class.
