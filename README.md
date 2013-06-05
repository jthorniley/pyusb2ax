# PyUSB2AX

The full documentation is now [here](http://jthorniley.github.io/pyusb2ax).

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

## Author

[James Thorniley](http://www.jamesthorniley.com)
