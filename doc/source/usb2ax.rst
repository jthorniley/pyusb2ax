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


  :param device_id:
    Where the device is located. E.g.
    the default (0) represents /dev/ttyACM0
  :type device_id: integer
  :param fix_sync_read_delay: Set to True if you plan to
    use 
    :py:func:`sync_read`. See :ref:`sync-read-detail` for
    more information.
  :type fix_sync_read_delay: boolean

  .. py:method:: write( servo_id, parameter, value )

    Write to :ref:`control table<control-tables>` of a single servo.

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

    Read a :ref:`control table <control-tables>`  entry from a single servo.

    :param servo_id: The bus ID of the servo to read from.
    :type servo_id: integer
    :param parameter: The control table point to write - a value allowed for the attached servo as listed in :ref:`control-tables`.
    :type parameter: string
    :returns: The value in the control table at the specified point
    :rtype: integer
    :raises ServoNotAttachedError: The servo with the given ID was not found on the bus when the object was created.
    :raises UnknownParameterError: The servo with the given ID does not support the parameter.

  .. py:method:: sync_write( servo_ids, parameter, values )

    Write to the :ref:`control tables <control-tables>` of several servos.

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

    Read from the :ref:`control tables <control-tables>` of several servos.

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

