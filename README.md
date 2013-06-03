# PyUSB2AX

A simple wrapper to access Dynamixel AX servos using the USB2AX interface under Linux.

_N.B. This is a python module that wraps a Linux C library - it will not help you access Dynamixels from other operating systems._

This is a build script and simple python module that allows you to easily control Dynamixel AX-12 servos (and possibly other models) using a [USB2AX](http://xevelabs.com/doku.php?id=product:usb2ax:usb2ax). It wraps the standard dynamixel C library available [here](http://support.robotis.com/en/software/dynamixel_sdk/usb2dynamixel/usb2dxl_linux.htm) after applying a patch to make it compatible with the USB2AX.

## Requirements

There should be no real requirements, but the file dynamixel.c is automatically generated using pybindgen if you delete it. However
you shouldn't need to do that as the one in the repository should be fine.

## Installation

    git clone git://github.com/jthorniley/pyusb2ax.git
    cd pyusb2ax
    python setup.py install
    
This does the following:

* Downloads the Dynamixel SDK
* Patches it to make it compatible with the USB2AX.
 * Specifically, that means turn the dxl_hal.c file into something more like Nicholas Saugnier's [modified verision](https://paranoidstudio.assembla.com/code/paranoidstudio/git/node/blob/master/usb2ax/soft/dxl_hal.c). This is useful/necessary because the USB2AX does not behave exactly the same as the USB2Dynamixel with the SDK expects.
* Generates and compiles a python module called **dynamixel** that wraps the C library straightforwardly.
* Installs a second module called **usb2ax** which can be used to access anything in **dynamixel** as well as some more helpful wrapper functions.

## Example

    import usb2ax
    
    usb2ax.dxl_initialize(0,1) # Expects to see the USB2AX at /dev/ttyACM0, with baud rate 1MBPS
    
    usb2ax.write(1,"goal_position",512) # Move the servo with ID 1 to position 512
                                        # (valid values are 0-1024, 512 is in the middle)
                                        
    print usb2ax.read(1,"present_position") # Prints the actual position reported by the dynamixel.

## Available commands

The library currently supports reading and writing via the above convention to
the following AX12 control table addresses. Details of these settings can be found
in the [AX12 manual](http://support.robotis.com/en/product/dynamixel/ax_series/dxl_ax_actuator.htm).

Note that usb2ax.write will fail if you try to write to one of the values that is
listed as read-only below.

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

## TODO

A nicer UI and better documentation.

Support for the [SYNC_READ](http://www.xevelabs.com/doku.php?id=product:usb2ax:advanced_instructions) command.
