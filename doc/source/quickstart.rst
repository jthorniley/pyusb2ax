Quick start
===========

Asynchronous access
-------------------

To use the library to do normal asynchronous reads and writes to the servos,
simply instantiate a :py:class:`usb2ax.Controller` using the with construction:

::
    
    with Controller() as dxl:
        
        try:
            actual_pos = dxl.read(1,"present_position")
            print "Servo 1 is currently at %d" % actual_pos
        except usb2ax.ReadError, e:
            print "There was an error reading from the dynamixel"

        #To move servo 1 to the middle
        #(Valid range is 0-1024)
        dxl.write(1,"goal_position",512)

Sync read/write
---------------

PyUSB2AX also supports the SYNC_READ instruction provided by the USB2AX. This
means you can make accesses to multiple servos rather quicker
using synchronous reads and writes across several servos.

::

    with Controller(fix_sync_read_delay=True) as dxl:

        #Moves servo 1 to 400 and servo 2 to 600
        dxl.sync_write([1,2],"goal_position",[400,600])

        #Give it a little time to actually move
        import time
        time.sleep(1.0)

        #Sync read should now tell us the final positions
        #of the servos.
        try:
            print dxl.sync_read([1,2],"present_position")
        except usb2ax.ReadError, e:
            print "There was an error performing the sync_read"

Note that when we initialized the :py:class:`usb2ax.Controller` we 
passed the argument `fix_sync_read_delay=True`. This will ensure that
the dynamixels are properly configured to support synchronous reads,
see :ref:`sync-read-detail` for more information.
