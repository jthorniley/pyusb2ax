from distutils.core import setup, Extension
import distutils.core
import distutils.command.build_ext

import pybindgen
from pybindgen import FileCodeSink
from pybindgen.gccxmlparser import ModuleParser

import subprocess
import os.path
import tempfile
import zipfile

patch = """diff -U 3 a/dxl_hal.c b/dxl_hal.c
--- a/dxl_hal.c	2013-06-03 17:40:45.405693506 +0100
+++ b/dxl_hal.c	2013-06-03 17:41:00.285834108 +0100
@@ -19,10 +19,9 @@
 int dxl_hal_open(int deviceIndex, float baudrate)
 {
 	struct termios newtio;
-	struct serial_struct serinfo;
 	char dev_name[100] = {0, };
 
-	sprintf(dev_name, "/dev/ttyUSB%d", deviceIndex);
+	sprintf(dev_name, "/dev/ttyACM%d", deviceIndex);
 
 	strcpy(gDeviceName, dev_name);
 	memset(&newtio, 0, sizeof(newtio));
@@ -33,7 +32,7 @@
 		goto DXL_HAL_OPEN_ERROR;
 	}
 
-	newtio.c_cflag		= B38400|CS8|CLOCAL|CREAD;
+	newtio.c_cflag		= B1000000|CS8|CLOCAL|CREAD;
 	newtio.c_iflag		= IGNPAR;
 	newtio.c_oflag		= 0;
 	newtio.c_lflag		= 0;
@@ -46,20 +45,6 @@
 	if(gSocket_fd == -1)
 		return 0;
 	
-	if(ioctl(gSocket_fd, TIOCGSERIAL, &serinfo) < 0) {
-		fprintf(stderr, "Cannot get serial info\\n");
-		return 0;
-	}
-	
-	serinfo.flags &= ~ASYNC_SPD_MASK;
-	serinfo.flags |= ASYNC_SPD_CUST;
-	serinfo.custom_divisor = serinfo.baud_base / baudrate;
-	
-	if(ioctl(gSocket_fd, TIOCSSERIAL, &serinfo) < 0) {
-		fprintf(stderr, "Cannot set serial info\\n");
-		return 0;
-	}
-	
 	dxl_hal_close();
 	
 	gfByteTransTime = (float)((1000.0f / baudrate) * 12.0f);
@@ -73,7 +58,7 @@
 		goto DXL_HAL_OPEN_ERROR;
 	}
 
-	newtio.c_cflag		= B38400|CS8|CLOCAL|CREAD;
+	newtio.c_cflag		= B1000000|CS8|CLOCAL|CREAD;
 	newtio.c_iflag		= IGNPAR;
 	newtio.c_oflag		= 0;
 	newtio.c_lflag		= 0;
@@ -99,25 +84,10 @@
 
 int dxl_hal_set_baud( float baudrate )
 {
-	struct serial_struct serinfo;
 	
 	if(gSocket_fd == -1)
 		return 0;
 	
-	if(ioctl(gSocket_fd, TIOCGSERIAL, &serinfo) < 0) {
-		fprintf(stderr, "Cannot get serial info\\n");
-		return 0;
-	}
-	
-	serinfo.flags &= ~ASYNC_SPD_MASK;
-	serinfo.flags |= ASYNC_SPD_CUST;
-	serinfo.custom_divisor = serinfo.baud_base / baudrate;
-	
-	if(ioctl(gSocket_fd, TIOCSSERIAL, &serinfo) < 0) {
-		fprintf(stderr, "Cannot set serial info\\n");
-		return 0;
-	}
-	
 	//dxl_hal_close();
 	//dxl_hal_open(gDeviceName, baudrate);
"""
 	
def dynamixel_gen():
    module_parser = ModuleParser("dynamixel","::")
    module = module_parser.parse(["DXL_SDK_LINUX_v1_01/include/dynamixel.h"])
    #pybindgen.write_preamble(FileCodeSink(sys.stdout))
    module.add_include('"dynamixel.h"')
    module.generate(FileCodeSink(open("dynamixel.c","w+")))

def patch_dxl_sdk():

    sp = subprocess.Popen(["patch","-N","-r","-","DXL_SDK_LINUX_v1_01/src/dxl_hal.c"],stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    print sp.communicate(input=patch)[0]

def download_dxl_sdk():
    if os.path.exists("DXL_SDK_LINUX_v1_01"):
        print "Dynamixel SDK already downloaded"
        return
    else:
        try:
            import pycurl
            curl = pycurl.Curl()
            curl.setopt(pycurl.URL, "http://support.robotis.com/en/baggage_files/dynamixel_sdk/dxl_sdk_linux_v1_01.zip" )
            with tempfile.TemporaryFile() as tmpfile:
                curl.setopt( pycurl.WRITEDATA,tmpfile )
                curl.perform()

                zf = zipfile.ZipFile( tmpfile, "r" )
                zf.extractall()
        except ImportError,e:
            print "PyCURL not found, trying to manually download"
            
            fname = tempfile.mkstemp()[1]

            try:
                subprocess.call(["curl","http://support.robotis.com/en/baggage_files/dynamixel_sdk/dxl_sdk_linux_v1_01.zip","-o",fname])

                zf = zipfile.ZipFile( fname, "r" )
                zf.extractall()

                os.unlink(fname)
            except:
                print "Could not run curl as subprocess, trying wget"
                try:
                    subprocess.call(["wget","http://support.robotis.com/en/baggage_files/dynamixel_sdk/dxl_sdk_linux_v1_01.zip","-O",fname])

                    zf = zipfile.ZipFile( fname, "r" )
                    zf.extractall()

                    os.unlink(fname)
                except Exception, e:
                    print """
****************************** FAIL ***********************************************
* I tried really hard but I could not download the dynamixel SDK. This
* could be due to lack of network connection or maybe you could try 
* installing curl or wget on your system.
*
* You will need to download it manually. It should be available at
*
* http://support.robotis.com/en/baggage_files/dynamixel_sdk/dxl_sdk_linux_v1_01.zip
*
* Once you have it, unzip it so that there is a directory called
* DXL_SDK_LINUX_v1_01 in the current directory and run 
*
* python setup.py build again.
*
**************************************************************************************
"""
                    raise e



class build_bindings(distutils.command.build_ext.build_ext):
    def run(self):
        
        download_dxl_sdk()
        patch_dxl_sdk()
        dynamixel_gen()
        
        distutils.command.build_ext.build_ext.run(self)

dynamixel_mod = Extension('dynamixel',
                    sources = ['DXL_SDK_LINUX_v1_01/src/dxl_hal.c',
                        'DXL_SDK_LINUX_v1_01/src/dynamixel.c',
                        'dynamixel.c'],
                    include_dirs = ['DXL_SDK_LINUX_v1_01/src/','DXL_SDK_LINUX_v1_01/include'])

setup (name = 'PyUSB2AX',
        version = '1.0',
        description = 'Python binding for controlling USB2AX',
        py_modules = ["usb2ax"],
        ext_modules = [dynamixel_mod],
        cmdclass = {"build_ext":build_bindings} )
