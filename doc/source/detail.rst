Detailed instructions
=====================

Initializing the USB2AX
-----------------------

When you physically connect the USB2AX, it registers itself in the
`/dev` diretory. In all probability it will register itself as
`/dev/ttyACM0`, however it may come up as `/dev/ttyACM1`. You can
check what has happened by pluggin it in and running dmesg,
from which you should get output like this:

.. code-block:: bash

    $ dmesg | grep -C 7 ACM
    [12917.687364] usb 3-3.4: new full-speed USB device number 66 using xhci_hcd
    [12917.700656] usb 3-3.4: New USB device found, idVendor=16d0, idProduct=06a7
    [12917.700662] usb 3-3.4: New USB device strings: Mfr=1, Product=2, SerialNumber=220
    [12917.700664] usb 3-3.4: Product: USB2AX
    [12917.700666] usb 3-3.4: Manufacturer: Xevelabs
    [12917.700668] usb 3-3.4: SerialNumber: 6403635373035121E161
    [12917.701516] usb 3-3.4: ep 0x82 - rounding interval to 1024 microframes, ep desc says 2040 microframes
    [12917.701784] cdc_acm 3-3.4:1.0: ttyACM0: USB ACM device

If the last line doesn't say `ttyACM0`, e.g. it says `ttyACM1`, then you will
need to initialize your controller with

::

    Controller(device_id=1)

Where the `device_id` is set to the number on the end of the device name shown.

Bus scanning
------------

When you instantiate a :py:class:`usb2ax.Controller` it will scan the bus for connected 
servos and print out information relating to them. For example you should see an
output like this:

::

    usb2ax: Initiating scan...
    usb2ax: USB2AX          : /dev/ttyACM0
    usb2ax: AX-12           : 1
    usb2ax: AX-12           : 2
    usb2ax: AX-12           : 3
    usb2ax: AX-12           : 4
    usb2ax: AX-12           : 5
    usb2ax: AX-12           : 6
    usb2ax: AX-12           : 16
    usb2ax: AX-12           : 17
    usb2ax: AX-12           : 18
    usb2ax: Model no.       : 16897
    usb2ax: Firmware version: 3
    usb2ax: Success!

You should see a line for every connected servo. The model no. and
firmware version at the end of the list relate to the USB2AX device
itself. If it is not the same as shown above, then you probably
have a different version of the device to the author, which is unlikely
to be a huge problem.

If you don't see all your servos listed this is likely to
be a problem. Ensure that your servos are set to
communicate at 1Mbps and that you do not have any ID conflicts --
the servos are all configured with ID 1 to start with. To change
this, you will need to connect each servo you are using one at a time,
and simply use

.. code-block:: python

    with Controller() as dxl:
        dxl.write(1,"id",[NEW ID])

.. _sync-read-detail:

Sync read delay timing
----------------------

If you use the :py:func:`sync_read` function you are advised to initialize the
controller with the `fix_sync_read_delay` argument set to True. You can take
this on trust ignore this section, but if you would like to know why read on.

The USB2AX 
`SYNC_READ <http://www.xevelabs.com/doku.php?id=product:usb2ax:advanced_instructions>`_
functionality supported by this library is a useful way to get quicker reads from multiple
servos. It allows the USB2AX device to send multiple read requests to 
different devices, then collate all the responses and send it back to the client
application as one packet. This reduces the latency introduced by the
USB to serial port conversion. 


When an individual READ instruction is sent to a servo, the servo waits a short
time to send a reply. This timing can be set in the servo's control
table. Out of the box, Dynamixel AX-12 servos have this set to a value
of 250. This appears to be an unreliable setting for use with the
SYNC_READ function. To fix this, you need to set this value to something
much lower. To make this easier, PyUSB2AX can do this automatically for
you when necessary if you simply set `fix_sync_read_delay` to True
when instantiating your `Controller`. This will (if necessary)
change the return delay settings for poorly configured dynamixels
to a value of 20. If you don't use `fix_sync_read_delay` and you
connect a dynamixel with the default delay time set, you may see an
output like this:

::

    usb2ax: Initiating scan...
    usb2ax: USB2AX          : /dev/ttyACM0
    usb2ax: AX-12           : 1
    usb2ax: Delay time is 250 -- you cannot use sync_read
    usb2ax: To fix this automatically call initialize with fix_sync_read_delay=True

If you see this message, then any calls to sync_read with throw a
`SyncReadError`. If you re-run with `fix_sync_read_delay=True` you will see

::

    usb2ax: Initiating scan...
    usb2ax: USB2AX          : /dev/ttyACM0
    usb2ax: AX-12           : 1
    usb2ax: INFO: Servo 1 return delay set to 20 to make compatible with sync_read


Now you can use `sync_read` freely.

Control tables
--------------

The servos are controlled by updated the control tables. Below are full references for
the control tables. The parameter name on the left most column can be used as arguments
to `read`, `write`, `sync_read` and `sync_write`. For example, if you pass
"goal_position" as the argument to `write`, we will update the control table
address 0x1E, which is listed as referencng the target position in the
Dynamixel `manual <http://support.robotis.com/en/product/dynamixel/ax_series/dxl_ax_actuator.htm>`_.


In theory at least we support both
AX-12/18 and MX-28T servos, which have slightly different control tables. Most
of the addresses are the same, so for example if you are writing to "goal_position"
it is not important.

In theory (this is untested) you can connect both AX and MX servos to the same bus.
You can even sync_read and sync_write to both types of servos at the same time,
provided you are accessing a parameter that is the same in both types of
servo. If you try to `write` to "goal_acceleration" on an AX-12 servo for example, you will
get a :py:class:`usb2ax.UnknownParameterError`, likewise if you try to
`sync_write` to "goal_acceleration" on a collection of servos where *any* of the
servos is an AX-12.

AX-12/18 Control table
^^^^^^^^^^^^^^^^^^^^^^

==========================   =====================    ================================
Parameter                    Control table address    Read-only (R) or Read/Write(R/W)
==========================   =====================    ================================
model_no                      0x00                                  R
firmware_version              0x02                                  R
id                            0x03                                  R/W
baud_rate                     0x04                                  R/W
return_delay_time             0x05                                  R/W
cw_angle_limit                0x06                                  R/W
ccw_angle_limit               0x08                                  R/W
high_limit_temp               0x0B                                  R/W
low_limit_voltage             0x0C                                  R/W
high_limit_voltage            0x0D                                  R/W
max_torque                    0x0E                                  R/W
status_return_level           0x10                                  R/W
alarm_led                     0x11                                  R/W
alarm_shutdown                0x12                                  R/W
torque_enable                 0x18                                  R/W
led                           0x19                                  R/W
cw_compliance_margin          0x1A                                  R/W
ccw_compliance_margin         0x1B                                  R/W
cw_compliance_slope           0x1C                                  R/W
ccw_compliance_slope          0x1D                                  R/W
goal_position                 0x1E                                  R/W
moving_speed                  0x20                                  R/W
torque_limit                  0x22                                  R/W
present_position              0x24                                  R
present_speed                 0x26                                  R
present_load                  0x28                                  R
present_voltage               0x2A                                  R
present_temp                  0x2A                                  R
registered                    0x2C                                  R
moving                        0x2E                                  R
lock                          0x2F                                  R/W
punch                         0x30                                  R/W
==========================   =====================    ================================


MX-28T Control table
^^^^^^^^^^^^^^^^^^^^


==========================   =====================    ================================
Parameter                    Control table address    Read-only (R) or Read/Write(R/W)
==========================   =====================    ================================
model_no                      0x00                                  R
firmware_version              0x02                                  R
id                            0x03                                  R/W
baud_rate                     0x04                                  R/W
return_delay_time             0x05                                  R/W
cw_angle_limit                0x06                                  R/W
ccw_angle_limit               0x08                                  R/W
high_limit_temp               0x0B                                  R/W
low_limit_voltage             0x0C                                  R/W
high_limit_voltage            0x0D                                  R/W
max_torque                    0x0E                                  R/W
status_return_level           0x10                                  R/W
alarm_led                     0x11                                  R/W
alarm_shutdown                0x12                                  R/W
torque_enable                 0x18                                  R/W
led                           0x19                                  R/W
d_gain                        0x1A                                  R/W
i_gain                        0x1B                                  R/W
p_gain                        0x1C                                  R/W
goal_position                 0x1E                                  R/W
moving_speed                  0x20                                  R/W
torque_limit                  0x22                                  R/W
present_position              0x24                                  R
present_speed                 0x26                                  R
present_load                  0x28                                  R
present_temp                  0x2A                                  R
present_voltage               0x2A                                  R
registered                    0x2C                                  R
moving                        0x2E                                  R
lock                          0x2F                                  R/W
punch                         0x30                                  R/W
goal_acceleration             0x49                                  R/W
==========================   =====================    ================================

