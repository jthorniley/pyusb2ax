Installation
============

Requirements
------------

Python 2.7 and Cython. You will also need the relevant hardware.

* One or more Dynamixel servos. This has been tested on the `Dynamixel AX-12 <http://www.robotis.com/xe/dynamixel_en>`_ but
  the MX-28T model *should* also work.
* The `USB2AX <http://xevelabs.com/doku.php?id=product:usb2ax:usb2ax>`_ interface device created by Xevelabs.
* Some way to power the servos, e.g. a separate battery or the `SMPS2Dynamixel <http://www.trossenrobotics.com/store/p/5886-SMPS2Dynamixel-Adapter.aspx>`_ adapter. 
  Refer to the Dynamixel `manual <http://support.robotis.com/en/product/dynamixel/ax_series/dxl_ax_actuator.htm>`_ or the USB2AX website for further help with setting up the hardware.





Building
--------

.. code-block:: bash

    $ git clone git://github.com/jthorniley/pyusb2ax.git
    $ cd pyusb2ax
    $ python setup.py install
    
This does the following:

* Downloads the Dynamixel SDK
* Patches it to make it compatible with the USB2AX.
    * Specifically, that means turn the dxl_hal.c file into something more like Nicholas Saugnier's `modified verision <https://paranoidstudio.assembla.com/code/paranoidstudio/git/node/blob/master/usb2ax/soft/dxl_hal.c>`_. This is useful/necessary because the USB2AX does not behave exactly the same as the USB2Dynamixel which the SDK expects.
    * And makes modifications to allow passing the sync_read instruction through the API.
* Creates and installs a module called :py:mod:`usb2ax` which provides easy access to the dynamixel servos from Python.





