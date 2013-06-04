API reference for usb2ax
========================

.. py:module:: usb2ax

.. py:function:: initialize( [device_id=0],[fix_sync_delay_time=False] )

  Initialize the connection to the USB2AX.

  :param device_id:
    Where the device is located. E.g.
    the default (0) represents /dev/ttyACM0
  :type device_id: integer
  :param fix_sync_read_delay: If True, automatically ensures
    that all connected dynamixels are configured correctly for
    using :py:func:`sync_read`. If this is False and :py:func:`sync_read`
    is called on a servo which is badly configured, an exception may
    be raised.
  :type fix_sync_read_delay: boolean

.. py:function:: write( servo_id, parameter, value )

  Write to control table of a single servo.

  For example, to move servo with ID 1 to its central
  point:

  >>> usb2ax.write( 1, "goal_position", 512 ) 

  :param servo_id: The bus ID of the servo to be written to.
  :type servo_id: integer
  :param parameter: The control table point to write.
  :type parameter: string
  :param value: The value to write.
  :type value: integer

.. py:function:: read( servo_id, parameter )

  Read control table from a single servo.

  For example, to read the baud rate of servo 1:
  
  >>> usb2ax.read( 1, "baud_rate" ) # Result should be 1 (corresponds to 1 MHz)
  1 

  :param servo_id: The bus ID of the servo to read from.
  :type servo_id: integer
  :param parameter: The control table point to read.
  :type parameter: string
  :returns: The value in the control table at the specified point
  :rtype: integer

.. py:function:: sync_write( servo_id, parameter, value )

  Write to the control tables of several servos.

  Supply a list of servo ids, which parameter you want to change, and
  a list of new values.

  For example, to move servo 1 to position 600 and servo 2 to position 400:

  >>> usb2ax.write( [1,2], "goal_position", [600,400] ) 

  :param servo_ids: The bus IDs of the servos to modify.
  :type servo_ids: iterable
  :param parameter: The control table point to write.
  :type parameter: string
  :param values: The values to write.
  :type values: iterable

.. py:function:: sync_read( servo_id, parameter, value )

  Read from the control tables of several servos.

  Supply a list of servo ids, which parameter you want to get.

  >>> usb2ax.read( [1,2], "id" ) 
  [1,2]

  :param servo_ids: The bus IDs of the servos to read from.
  :type servo_ids: iterable
  :param parameter: The control table point to read.
  :type parameter: string
  :returns: A list of values from the servos specified.
  :rtype: list

.. py:function:: reset_usb2ax( [device_id=0] )

  Reset the USB2AX device. Call this instead of (not as well as)
  :py:func:`initialize`. It will cause the USB2AX device to
  reset which can be useful if it has got into a non-working state.
  The green LED should go off then come back on again after a few
  seconds.


