# PyUSB2AX

A simple wrapper to access Dynamixel AX servos using the USB2AX interface under Linux.

_N.B. This is a python module that wraps a Linux C library - it will not help you access Dynamixels from other operating systems._

This is a build script and simple python module that allows you to easily control Dynamixel AX-12 servos (and possibly other models) using a 
Xevelabs [USB2AX](http://xevelabs.com/doku.php?id=product:usb2ax:usb2ax). It wraps the standard dynamixel C library 
available [here](http://support.robotis.com/en/software/dynamixel_sdk/usb2dynamixel/usb2dxl_linux.htm) after applying 
a patch to make it compatible with the USB2AX.

A particular advantage of this is that in addition to the funtionality you would expect this library
also supports the 
[SYNC_READ](http://www.xevelabs.com/doku.php?id=product:usb2ax:advanced_instructions) 
command that the USB2AX provides for faster reads from multiple servos.

## Requirements

Python 2.7 and Cython. You will also need the relevant hardware: one or more [Dynamixel AX-12](http://www.robotis.com/xe/dynamixel_en) type servos, the excellent and tiny [USB2AX](http://xevelabs.com/doku.php?id=product:usb2ax:usb2ax) interface device created by Xevelabs, and some way to power them, e.g. a separate battery or the [SMPS2Dynamixel](http://www.trossenrobotics.com/store/p/5886-SMPS2Dynamixel-Adapter.aspx) adapter. Refer to the Dynamixel [manual](http://support.robotis.com/en/product/dynamixel/ax_series/dxl_ax_actuator.htm) or the USB2AX website for further help with setting up the hardware.

## Installation

    git clone git://github.com/jthorniley/pyusb2ax.git
    cd pyusb2ax
    python setup.py install
    
This does the following:

* Downloads the Dynamixel SDK
* Patches it to make it compatible with the USB2AX.
 * Specifically, that means turn the dxl\_hal.c file into something more like Nicholas Saugnier's [modified verision](https://paranoidstudio.assembla.com/code/paranoidstudio/git/node/blob/master/usb2ax/soft/dxl_hal.c). This is useful/necessary because the USB2AX does not behave exactly the same as the USB2Dynamixel which the SDK expects.
 * And makes modifications to allow passing the sync\_read instruction through the API.
* Creates a module called <tt>usb2ax</tt> which provides easy access to the dynamixel library from Python via the
  methods illustrated below.

## Example

### Serial read/write
```python
import usb2ax

try:
  usb2ax.initialize(0) # Expects to see the USB2AX at /dev/ttyACM0
  usb2ax.write(1,"goal_position",512) # Move the servo with ID 1 to position 512
                                      # (valid values are 0-1024, 512 is in the middle)

  print usb2ax.read(1,"present_position") # Prints the actual position reported by the dynamixel.
finally:
  usb2ax.terminate() # Shut down the connection neatly
```

### Sync read/write

Note that sync read/write should generally be faster.

See the file [example.py](https://github.com/jthorniley/pyusb2ax/blob/master/example.py) for another usage of this.

```python    
import usb2ax

try:
  usb2ax.initialize(0, fix_sync_read_delay=True)

  usb2ax.sync_write([1,2],"goal_position",[600,400]) # Move servo 1 to 600 and servo 2 to 400
  data = usb2ax.sync_read([1,2],"present_position") # Sync read
  print data[0] # Position of servo 1
  print data[1] # Position of servo 2
finally:
  usb2ax.terminate() # Shut down the connection neatly
```

## Available commands

The library currently supports reading and writing via the above convention to
the following AX12 control table addresses. Details of these settings can be found
in the [AX12 manual](http://support.robotis.com/en/product/dynamixel/ax_series/dxl_ax_actuator.htm).

The <tt>read</tt> and <tt>write</tt> functions will raise exceptions if you
try to access something not listed below, or try to write to something listed
as read-only.


<table>
<tr><th>Parameter</th><th>Control table address</th><th>Read-only (R) or Read/Write(R/W)</th></tr>
<tr><td>model_no</td><td>0x00</td><td>R</td></tr>
<tr><td>firmware_version</td><td>0x02</td><td>R</td></tr>
<tr><td>id</td><td>0x03</td><td>R/W</td></tr>
<tr><td>baud_rate</td><td>0x04</td><td>R/W</td></tr>
<tr><td>return_delay_time</td><td>0x05</td><td>R/W</td></tr>
<tr><td>cw_angle_limit</td><td>0x06</td><td>R/W</td></tr>
<tr><td>ccw_angle_limit</td><td>0x08</td><td>R/W</td></tr>
<tr><td>max_torque</td><td>0x0e</td><td>R/W</td></tr>
<tr><td>torque_enable</td><td>0x18</td><td>R/W</td></tr>
<tr><td>cw_compliance_margin</td><td>0x1a</td><td>R/W</td></tr>
<tr><td>ccw_compliance_margin</td><td>0x1b</td><td>R/W</td></tr>
<tr><td>cw_compliance_slope</td><td>0x1c</td><td>R/W</td></tr>
<tr><td>ccw_compliance_slope</td><td>0x1d</td><td>R/W</td></tr>
<tr><td>goal_position</td><td>0x1e</td><td>R/W</td></tr>
<tr><td>moving_speed</td><td>0x20</td><td>R/W</td></tr>
<tr><td>torque_limit</td><td>0x22</td><td>R/W</td></tr>
<tr><td>present_position</td><td>0x24</td><td>R</td></tr>
<tr><td>present_speed</td><td>0x26</td><td>R</td></tr>
<tr><td>present_load</td><td>0x28</td><td>R</td></tr>
<tr><td>punch</td><td>0x30</td><td>R/W</td></tr>
</table>

## Troubleshooting

### Baud rate

Currently you can only use the 1Mhz baud rate setting. This is the default setting for most AX 12 servos. If yours is set to something else, you will need to change it via some other method by writing 1 to the control table address 0x04.

### Hardware checks

Make sure that

* The USB2AX is plugged into the USB port.
* There should be a green LED lit up on the USB2AX
* You have properly connected all the 3-wire serial connections.
* You have properly connected the power to the dynamixels. Remember that the USB2AX does not supply power to the motors, you have to connect that up separately (the USB2AX website has more information).
 * When you plug the power in, a red LED on the back of the servo should light up briefly.
* The red LED on the back of the servo should NOT be flashing permanently -- it should only light up briefly once when you connect the power. If it flashing that means the servo is in an error state. You can usually fix this by disconnecting then reconnecting the power.

### Connection problems

If you get this error message:

    usb2ax.InitError: There was a problem connecting to the USB2AX at /dev/ttyACM0

Try first running dmesg to check that the USB2AX is connecting correctly, you should see something
like

    [ 9216.979357] usb 3-3.3: new full-speed USB device number 21 using xhci_hcd
    [ 9216.992828] usb 3-3.3: New USB device found, idVendor=16d0, idProduct=06a7
    [ 9216.992839] usb 3-3.3: New USB device strings: Mfr=1, Product=2, SerialNumber=220
    [ 9216.992845] usb 3-3.3: Product: USB2AX
    [ 9216.992849] usb 3-3.3: Manufacturer: Xevelabs
    [ 9216.992853] usb 3-3.3: SerialNumber: 6403635373035121E161
    [ 9216.993668] usb 3-3.3: ep 0x82 - rounding interval to 1024 microframes, ep desc says 2040 microframes
    [ 9216.994410] cdc_acm 3-3.3:1.0: ttyACM0: USB ACM device

If it hasn't connected, try the USB2AX [website](http://xevelabs.com/doku.php?id=product:usb2ax:usb2ax) for some help.

Note the name <tt>ttyACM0</tt> -- if you get something else like <tt>ttyACM1</tt> then
you need to call <tt>usb2ax.initialize(1)</tt>.

Check the permissions on the device. You will probably see something like this:

    $ ls -lh /dev/ttyACM0 
    crw-rw----. 1 root dialout 166, 0 Jun  4 11:55 /dev/ttyACM0

Note the group name <tt>dialout</tt>. Check your user's current groups with <tt>groups</tt>.
You may need to add your user to the dialout group:

    $ usermod -a -G dialout <your_username>

The group change only takes effect when you login. So either logout then in again, or if you are in
a terminal you can do <tt>su - your\_username</tt> to get a new login session.

Finally, if you have modem-manager running (which might be the case on complete desktop
Linux installs, probably less likely to be a problem on Raspberry Pi etc), it
may lock access to the serial port. Try
<tt>sudo killall modem-manager</tt>. If that works, you may be able to get rid of it permanently by doing

    $ cd /usr/share/dbus-1/system-services
    $ mv org.freedesktop.ModemManager.service org.freedesktop.ModemManager.service.disabled

If you still have problems, check if anything else is locking the serial port with

    $ sudo lsof | grep ACM

The output of this should ideally be nothing. If it isn't, try and get rid of whatever is there.

## TODO

Support all the parameter settings.

Better documentation.

Interface for setting angles in radians.


## Author

[James Thorniley](http://www.jamesthorniley.com)
