from distutils.core import setup, Extension
import distutils.core
from Cython.Distutils import build_ext


import subprocess
import os.path
import tempfile
import zipfile

patch = """diff DXL_SDK_LINUX_v1_01/include/dynamixel.h DXL_SDK_LINUX_v1_01/include/dynamixel.h
index 8a8ed70..270cfc6 100644
--- DXL_SDK_LINUX_v1_01/include/dynamixel.h
+++ DXL_SDK_LINUX_v1_01/include/dynamixel.h
@@ -26,6 +26,7 @@ void dxl_set_txpacket_instruction(int instruction);
 #define INST_ACTION			(5)\r
 #define INST_RESET			(6)\r
 #define INST_SYNC_WRITE		(131)\r
+#define INST_SYNC_READ		(132)\r
 \r
 void dxl_set_txpacket_parameter(int index, int value);\r
 void dxl_set_txpacket_length(int length);\r
diff DXL_SDK_LINUX_v1_01/src/dxl_hal.c DXL_SDK_LINUX_v1_01/src/dxl_hal.c
index d78c468..26b3e08 100644
--- DXL_SDK_LINUX_v1_01/src/dxl_hal.c
+++ DXL_SDK_LINUX_v1_01/src/dxl_hal.c
@@ -19,10 +19,9 @@ char	gDeviceName[20];
 int dxl_hal_open(int deviceIndex, float baudrate)
 {
 	struct termios newtio;
-	struct serial_struct serinfo;
 	char dev_name[100] = {0, };
 
-	sprintf(dev_name, "/dev/ttyUSB%d", deviceIndex);
+	sprintf(dev_name, "/dev/ttyACM%d", deviceIndex);
 
 	strcpy(gDeviceName, dev_name);
 	memset(&newtio, 0, sizeof(newtio));
@@ -33,7 +32,7 @@ int dxl_hal_open(int deviceIndex, float baudrate)
 		goto DXL_HAL_OPEN_ERROR;
 	}
 
-	newtio.c_cflag		= B38400|CS8|CLOCAL|CREAD;
+	newtio.c_cflag		= B1000000|CS8|CLOCAL|CREAD;
 	newtio.c_iflag		= IGNPAR;
 	newtio.c_oflag		= 0;
 	newtio.c_lflag		= 0;
@@ -46,20 +45,6 @@ int dxl_hal_open(int deviceIndex, float baudrate)
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
@@ -73,7 +58,7 @@ int dxl_hal_open(int deviceIndex, float baudrate)
 		goto DXL_HAL_OPEN_ERROR;
 	}
 
-	newtio.c_cflag		= B38400|CS8|CLOCAL|CREAD;
+	newtio.c_cflag		= B1000000|CS8|CLOCAL|CREAD;
 	newtio.c_iflag		= IGNPAR;
 	newtio.c_oflag		= 0;
 	newtio.c_lflag		= 0;
@@ -99,25 +84,10 @@ void dxl_hal_close()
 
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
 	
diff DXL_SDK_LINUX_v1_01/src/dynamixel.c DXL_SDK_LINUX_v1_01/src/dynamixel.c
index 3800c18..d292caf 100644
--- DXL_SDK_LINUX_v1_01/src/dynamixel.c
+++ DXL_SDK_LINUX_v1_01/src/dynamixel.c
@@ -58,7 +58,8 @@ void dxl_tx_packet(void)
 		&& gbInstructionPacket[INSTRUCTION] != INST_REG_WRITE
 		&& gbInstructionPacket[INSTRUCTION] != INST_ACTION
 		&& gbInstructionPacket[INSTRUCTION] != INST_RESET
-		&& gbInstructionPacket[INSTRUCTION] != INST_SYNC_WRITE )
+		&& gbInstructionPacket[INSTRUCTION] != INST_SYNC_WRITE 
+    && gbInstructionPacket[INSTRUCTION] != INST_SYNC_READ )
 	{
 		gbCommStatus = COMM_TXERROR;
 		giBusUsing = 0;
@@ -84,7 +85,8 @@ void dxl_tx_packet(void)
 		return;
 	}
 
-	if( gbInstructionPacket[INSTRUCTION] == INST_READ )
+	if( gbInstructionPacket[INSTRUCTION] == INST_READ ||
+          gbInstructionPacket[INSTRUCTION] == INST_SYNC_READ )
 		dxl_hal_set_timeout( gbInstructionPacket[PARAMETER+1] + 6 );
 	else
 		dxl_hal_set_timeout( 6 );
"""
 	
def patch_dxl_sdk():

    sp = subprocess.Popen(["patch","-N","-r","-","-p0"],stdin=subprocess.PIPE, stdout=subprocess.PIPE)
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



class build_bindings(build_ext):
    def run(self):
        
        download_dxl_sdk()
        patch_dxl_sdk()
        
        build_ext.run(self)

dynamixel_mod = Extension('usb2ax',
                    sources = ['DXL_SDK_LINUX_v1_01/src/dxl_hal.c',
                        'DXL_SDK_LINUX_v1_01/src/dynamixel.c',
                        'usb2ax.pyx'],
                    include_dirs = ['DXL_SDK_LINUX_v1_01/src/','DXL_SDK_LINUX_v1_01/include'])

setup (name = 'PyUSB2AX',
        version = '1.0',
        description = 'Python binding for controlling USB2AX',
        ext_modules = [dynamixel_mod],
        cmdclass = {"build_ext":build_bindings} )
