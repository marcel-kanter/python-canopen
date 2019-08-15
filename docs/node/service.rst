Service
=======

The ``Service`` class is the base class for all services of a ``Node``.

It can be attached to a ``Node`` or detached from it.

Attach/detach
-------------

The attach/detach pattern is used create a link from the ``Service`` (child) to the ``Node`` (parent). It only creates a functional relationship between them.
The structural relation between the child and the parent is handled by other means. 

Callbacks
---------

Callbacks are used to inform the application about events. After the application has added its callback function(s) to the service, they get called when an event occured.
The first argument for th callback is the event name, the rest of the arguments depend on the implementation of the sub-class.
