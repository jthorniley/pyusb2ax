# PyUSB2AX

A simple wrapper to access Dynamixel AX servos using the USB2AX interface under Linux.

N.B. This is a python module that wraps a Linux C library - it will not help you access Dynamixel's from other operating systems.

This is a build script and simple python module that allows you to easily control Dynamixel AX-12 servos (and possibly other models) using a [USB2AX](http://xevelabs.com/doku.php?id=product:usb2ax:usb2ax). It wraps the standard dynamixel C library available [here](http://support.robotis.com/en/software/dynamixel_sdk/usb2dynamixel/usb2dxl_linux.htm) after applying a patch to make it compatible with the USB2AX.

## Requirements

This uses pybindgen, which in turn relies on gccxml and pygccxml to generate bindings from C code.

## Installation

    git clone https://github.com/jthorniley/pyusb2ax.git
    cd pyusb2ax
    python setup.py install
    
This does the following:

* Downloads the Dynamixel SDK
* Patches it to make it compatible with the USB2AX.
 * Specifically, that means turn the dxl_hal.c file into something more like Nicholas Saugnier's [modified verision](https://paranoidstudio.assembla.com/code/paranoidstudio/git/node/blob/master/usb2ax/soft/dxl_hal.c)
* Generates and compiles a python module called **dynamixel** that wraps the C library straightforwardly.
* Installs a second module called **usb2ax** which can be used to access anything in **dynamixel** as well as some more helpful wrapper functions.

## Example

    import usb2ax
    
    usb2ax.dxl_initialize(0,1) # Expects to see the USB2AX at /dev/ttyACM0, with baud rate 1MBPS
    
    usb2ax.write(1,"goal_position",512) # Move the servo with ID 1 to position 512
                                        # (valid values are 0-1024, 512 is in the middle)
                                        
    print usb2ax.read(1,"present_position") # Prints the actual position reported by the dynamixel.
