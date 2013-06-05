Detailed instructions
=====================

Initializing the USB2AX
-----------------------

On being plugged in, the USB2AX registers itself in the
`/dev` directory. In all probability it will register itself as
`/dev/ttyACM0`, however it may come up as `/dev/ttyACM1`.
Running dmesg will help debug any problems:

.. code-block:: bash

    $ dmesg | grep -B 7 ACM
    [12917.687364] usb 3-3.4: new full-speed USB device number 66 using xhci_hcd
    [12917.700656] usb 3-3.4: New USB device found, idVendor=16d0, idProduct=06a7
    [12917.700662] usb 3-3.4: New USB device strings: Mfr=1, Product=2, SerialNumber=220
    [12917.700664] usb 3-3.4: Product: USB2AX
    [12917.700666] usb 3-3.4: Manufacturer: Xevelabs
    [12917.700668] usb 3-3.4: SerialNumber: 6403635373035121E161
    [12917.701516] usb 3-3.4: ep 0x82 - rounding interval to 1024 microframes, ep desc says 2040 microframes
    [12917.701784] cdc_acm 3-3.4:1.0: ttyACM0: USB ACM device

In the above output, the device has registered as `ttyACM0` -- the device ID is thus
0 and the interface can be initialized with the default constructor

::

    Controller()

Or ::

    Controller(device_id=0)
  

Otherwise, initialize the Controller with the indicated device_id, e.g. for `ttyACM1`

::

    Controller(device_id=1)

Bus scanning
------------

When you instantiate a :py:class:`usb2ax.Controller` it will scan the bus for connected 
servos and print out information relating to them. A typical output looks like this:

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

There should be a line for every connected servo. The model no. and
firmware version at the end of the list relate to the USB2AX device
itself. 

If not all of the expected  servos are listed that is likely to
be a problem. Ensure that all servos are set to
communicate at 1Mbps and that there are no ID conflicts --
the servos are all configured with ID 1 to start with. To change
this, connect each servo one at a time,
and simply use

.. code-block:: python

    with Controller() as dxl:
        dxl.write(1,"id",<NEW ID>)

.. _sync-read-detail:

Sync read delay timing
----------------------

When using the :py:func:`sync_read` function it is best to initialize the
controller with the `fix_sync_read_delay` argument set to True. You can take
this on trust and ignore this section, but if you would like to know why read on.

The USB2AX 
`SYNC_READ <http://www.xevelabs.com/doku.php?id=product:usb2ax:advanced_instructions>`_
functionality supported by this library is a useful way to get quicker reads from multiple
servos. It allows the USB2AX device to send multiple read requests to 
different devices, then collate all the responses and send it back to the client
application as one packet. This reduces the latency introduced by the
USB to serial port conversion. 


When an individual READ instruction is sent to a servo, the servo waits a short
time to send a reply. This timing can be set in the servo's control
table. By default, Dynamixel AX-12 servos have this set to a value
of 250. This appears to be an unreliable setting for use with the
SYNC_READ function -- ideally it should be much lower.
To avoid any problems, PyUSB2AX can fix the return delay time 
setting
when necessary if `fix_sync_read_delay` is set to True
when instantiating :py:class:`usb2ax.Controller`. This will (if necessary)
change the return delay settings for poorly configured dynamixels
to a sensible value. If `fix_sync_read_delay` is False and a poorly configured
dynamixel is connected, you may see an
output like this:

::

    usb2ax: Initiating scan...
    usb2ax: USB2AX          : /dev/ttyACM0
    usb2ax: AX-12           : 1
    usb2ax: Delay time is 250 -- you cannot use sync_read
    usb2ax: To fix this automatically call initialize with fix_sync_read_delay=True

Any calls to sync_read with throw a
`SyncReadError`. Running with `fix_sync_read_delay=True` produces

::

    usb2ax: Initiating scan...
    usb2ax: USB2AX          : /dev/ttyACM0
    usb2ax: AX-12           : 1
    usb2ax: INFO: Servo 1 return delay set to 1 to make compatible with sync_read


After this, `sync_read` should work with no problems.

.. _control-tables:

Control tables
--------------

The Dynamixel servos have internal control tables which are used for control.
The tables below show the parameters that can be read and written via these
tables.
The parameter name can be used as an argument
to `read`, `write`, `sync_read` and `sync_write`. For example, if you pass
"goal_position" as the argument to `write`, the control table
address 0x1E will be updated, causing the servo to move to the specified
position. Details of the meaning of each control table parameter
are given in the 
Dynamixel `manual <http://support.robotis.com/en/product/dynamixel/ax_series/dxl_ax_actuator.htm>`_.


PyUSB2AX should support 
AX-12/18 and MX-28T servos, which have slightly different control tables. Most
of the addresses are the same, so for example if writing to "goal_position"
it is not important what model of servo is attached.

In theory (this is untested) this library can talk to both AX and MX servos to the same bus.
It can even sync_read and sync_write to both types of servos at the same time,
provided the parameter addressed is the same in both types of
servo. Calling `write` to "goal_acceleration" on an AX-12 servo for example will
raise
a :py:class:`usb2ax.UnknownParameterError`. This error will also appear if 
`sync_write` is called with the parameter "goal_acceleration" on a collection of 
servos where *any* of the
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

