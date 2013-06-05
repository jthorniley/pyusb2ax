.. PyUSB2AX documentation master file, created by
   sphinx-quickstart on Tue Jun  4 20:27:34 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to PyUSB2AX's documentation!
====================================

A simple wrapper to access Dynamixel AX servos using the USB2AX interface under Linux.

*N.B. This is a python module that wraps a Linux C library - it will not help you access Dynamixels from other operating systems.*

This is a build script and simple python module that allows you to easily control Dynamixel AX-12 servos (and possibly other models) using a 
Xevelabs `USB2AX <http://xevelabs.com/doku.php?id=product:usb2ax:usb2ax>`_. It wraps the standard dynamixel C library 
available `here <http://support.robotis.com/en/software/dynamixel_sdk/usb2dynamixel/usb2dxl_linux.htm>`_ after applying 
a patch to make it compatible with the USB2AX.

A particular advantage of this is that in addition to the funtionality you would expect this library
also supports the 
`SYNC_READ <http://www.xevelabs.com/doku.php?id=product:usb2ax:advanced_instructions>`_
command that the USB2AX provides for faster reads from multiple servos.

Contents:

.. toctree::
   :maxdepth: 2

   installation
   quickstart
   detail
   usb2ax



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

