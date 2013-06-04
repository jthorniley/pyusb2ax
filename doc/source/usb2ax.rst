API reference for usb2ax
========================

.. py:function:: initialize( [device_id=0],[fix_sync_delay_time=False] )

  Initialize the connection to the USB2AX.

  :param device_id:
    Where the device is located. E.g.
    the default (0) represents /dev/ttyACM0
  :type device_id: integer
  :param fix_sync_read_delay: If true, we will ensure at startup
    that all connected dynamixels are configured correctly for
    using the sync_read command.
  :type fix_sync_read_delay: boolean
