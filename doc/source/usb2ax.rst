API reference for usb2ax
========================

.. py:module:: usb2ax

.. py:class:: Controller( [device_id=0],[fix_sync_delay_time=False] )

  Initialize the connection to the USB2AX.

  This will set up the serial port and scan for servo devices attached
  to the bus. You should have all the servos you want to use attached
  and switched on before calling this.

  Suggested usage:

  .. code-block:: python

     with Controller(device_id=0,fix_sync_read_delay=True) as dxl:
       do stuff...

  The `fix_sync_read_delay` argument should probably
  be set to True. It will change the return delay time
  setting for each Dynamixel to something compatible
  with the USB2AX SYNC_READ function if necessary. It is set to False by
  default so as not to unexpectedly change entries in the
  control tables of 
  attached servos.

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

  .. py:method:: write( servo_id, parameter, value )

    Write to control table of a single servo.

    For example, to move servo with ID 1 to its central
    point:

    ::
     
      with Controller() as dxl:
        dxl.write( 1, "goal_position", 512 ) 

    :param servo_id: The bus ID of the servo to be written to.
    :type servo_id: integer
    :param parameter: The control table point to write - a value allowed for the attached servo as listed in :ref:`control-tables`.
    :type parameter: string
    :param value: The value to write.
    :type value: integer
    :raises ServoNotAttachedError: The servo with the given ID was not found on the bus when the object was created.
    :raises UnknownParameterError: The servo with the given ID does not support the parameter.
    :raises InvalidWriteParameterError: The parameter cannot be written because it is read-only.

  .. py:method:: read( servo_id, parameter )

    Read control table entry from a single servo.

    :param servo_id: The bus ID of the servo to read from.
    :type servo_id: integer
    :param parameter: The control table point to write - a value allowed for the attached servo as listed in :ref:`control-tables`.
    :type parameter: string
    :returns: The value in the control table at the specified point
    :rtype: integer
    :raises ServoNotAttachedError: The servo with the given ID was not found on the bus when the object was created.
    :raises UnknownParameterError: The servo with the given ID does not support the parameter.

  .. py:method:: sync_write( servo_ids, parameter, values )

    Write to the control tables of several servos.

    Supply a list of servo ids, which parameter you want to change, and
    a list of new values.

    For example, to move servo 1 to position 600 and servo 2 to position 400:

    ::

      with Controller() as dxl:
        dxl.sync_write( [1,2], "goal_position", [600,400] ) 

    :param servo_ids: The bus IDs of the servos to modify.
    :type servo_ids: iterable
    :param parameter: The control table point to write - a value allowed for the attached servo as listed in :ref:`control-tables`.
    :type parameter: string
    :param values: The values to write.
    :type values: iterable
    :raises ServoNotAttachedError: At least one of the servos specified was not found on the bus when the object was created.
    :raises UnknownParameterError: At least one of the servos specified does not support the parameter.
    :raises InvalidWriteParameterError: The parameter cannot be written because it is read-only.

  .. py:method:: sync_read( servo_id, parameter, value )

    Read from the control tables of several servos.

    Supply a list of servo ids, which parameter you want to get.

    ::
      with Controller(fix_sync_read_delay=True) as dxl:
        usb2ax.sync_read( [1,2], "id" ) # Returns [1,2]

    :param servo_ids: The bus IDs of the servos to read from.
    :type servo_ids: iterable
    :param parameter: The control table point to write - a value allowed for the attached servo as listed in :ref:`control-tables`.
    :type parameter: string
    :returns: A list of values from the servos specified.
    :rtype: list
    :raises ServoNotAttachedError: At least one of the servos specified was not found on the bus when the object was created.
    :raises UnknownParameterError: At least one of the servos specified does not support the parameter.

.. py:function:: reset_usb2ax( [device_id=0] )

  Reset the USB2AX device itself (rather than the attached servos).
  If this is successful the LED on the USB2AX will turn off for a few
  seconds then turn back on.

