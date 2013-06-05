
import sys
from time import sleep

ERRBIT_VOLTAGE		 = 1
ERRBIT_ANGLE		 = 2
ERRBIT_OVERHEAT		 = 4
ERRBIT_RANGE		 = 8
ERRBIT_CHECKSUM		 = 16
ERRBIT_OVERLOAD		 = 32
ERRBIT_INSTRUCTION	 = 64

COMM_TXSUCCESS = 0
COMM_RXSUCCESS = 1
COMM_TXFAIL = 2
COMM_RXFAIL = 3
COMM_TXERROR = 4
COMM_RXWAITING = 5
COMM_RXTIMEOUT = 6
COMM_RXCORRUPT = 7
COMM_SYNC_READ_FAIL = 100

MMAP={
    "model_no":[0x00,2,False],
    "firmware_version":[0x02,1,False],
    "id":[0x03,1,True],
    "baud_rate":[0x04,1,True],
    "return_delay_time":[0x05,1,True],
    "cw_angle_limit":[0x06,2,True],
    "ccw_angle_limit":[0x08,2,True],

    "max_torque":[0x0E,2,True],
    "torque_enable":[0x18,1,True],
    "cw_compliance_margin":[0x1A,1,True],
    "ccw_compliance_margin":[0x1B,1,True],
    "cw_compliance_slope":[0x1C,1,True],
    "ccw_compliance_slope":[0x1D,1,True],
    "goal_position":[0x1E,2,True],
    "moving_speed":[0x20,2,True],
    "torque_limit":[0x22,2,True],
    "present_position":[0x24,2,False],
    "present_speed":[0x26,2,False],
    "present_load":[0x28,2,False],
    "punch":[0x30,2,True]
    }


cdef extern from "dynamixel.h":
    int dxl_initialize( int deviceIndex, int baudnum )
    void dxl_terminate()
    void dxl_set_txpacket_id(int id)
    void dxl_set_txpacket_instruction(int instruction)
    void dxl_set_txpacket_parameter(int index, int value)
    void dxl_set_txpacket_length(int length)

    int dxl_get_rxpacket_error(int errbit)

    int dxl_get_rxpacket_length()
    int dxl_get_rxpacket_parameter(int index)

    int dxl_makeword(int lowbyte, int highbyte)
    int dxl_get_lowbyte(int word)
    int dxl_get_highbyte(int word)
    void dxl_tx_packet()
    void dxl_rx_packet()
    void dxl_txrx_packet()

    int dxl_get_result()
    void dxl_ping(int id)
    int dxl_read_byte(int id, int address)
    void dxl_write_byte(int id, int address, int value)
    int dxl_read_word(int id, int address)
    void dxl_write_word(int id, int address, int value)

cdef check_rx_error():
    if dxl_get_rxpacket_error(ERRBIT_VOLTAGE):
        print "Voltage error"
    if dxl_get_rxpacket_error(ERRBIT_ANGLE ):
        print "Angle error"
    if dxl_get_rxpacket_error(ERRBIT_OVERHEAT):
        print "Overheat error"
    if dxl_get_rxpacket_error(ERRBIT_RANGE):
        print "Range error"
    if dxl_get_rxpacket_error(ERRBIT_CHECKSUM):
        print "Checksum error"
    if dxl_get_rxpacket_error(ERRBIT_OVERLOAD): 
        print "Overload error"
    if dxl_get_rxpacket_error(ERRBIT_INSTRUCTION): 
        print "Instruction error"
     

class InitError(Exception):
    def __init__(self, device_id):
        self.message = "There was a problem connecting to the USB2AX at /dev/ttyACM%d" % device_id

    def __str__(self):
        return self.message

class ReadError(Exception):
    def __init__(self,error_id):
        self.error_id = error_id

    def __str__(self):
        return str(self.error_id)

class UnknownParameterError(Exception):
    pass

class InvalidWriteParameterError(Exception):
    pass

class SyncReadError(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return """You tried to sync read but some of your devices
are set to return too slowly. To fix this call initialize with
fix_sync_read_delay = True.
"""

def reset_usb2ax(device_id=0):
    """
    Reset the usb2ax device.
    """

    result = dxl_initialize(device_id,1)
    if result == 0:
        raise InitError(device_id)

    dxl_set_txpacket_id(253) #USB2AX special ID
    dxl_set_txpacket_instruction(0x06) # RESET
    dxl_set_txpacket_length(2)
    dxl_tx_packet()
    status = dxl_get_result()

    print "Device reset, you should unplug it and plug it back in again"

cdef _read(int servo_id, int address, int length):

    cdef int result
    cdef int status


    func = dxl_read_byte
    if length == 2:
        func = dxl_read_word

    result = func(servo_id, address )
    status = dxl_get_result()
    if ( status == 1):
        return result
    else:
        raise ReadError(status)


class Controller:

    def __init__(self, device_id=0, fix_sync_read_delay = False):
        """
        Connect to the USB2AX device.

        Call this before calling anything else.

        The argument goes specifies which ACM device is the
        USB2AX. For example, if the USB2AX is at /dev/ttyACM0,
        call initialize(0) or initialize() (0 is the default
        argument).

        Raises InitError if there was a problem.
        """

        self.sync_read_ok = True

        result = dxl_initialize(device_id,1)
        if result == 0:
            raise InitError(device_id)


        sys.stderr.write("""usb2ax: Initiating scan...
usb2ax: USB2AX          : /dev/ttyACM%d
"""% device_id)
        no_devices_connected = True
        for i in range(1,253):

            try:
                model = self.read(i, "model_no")

                if model in [12,18]:
                    model = "AX-%d   " % model
                elif model == 29:
                    model = "MX-%dT  " % model
                else:
                    model = "Model %d" % model
                sys.stderr.write("usb2ax: %s        : %d\n" % (model, i))
                no_devices_connected =False
                try:
                    delay = self.read(i,"return_delay_time")
                    if delay > 20:
                        if fix_sync_read_delay:
                            self.write(i,"return_delay_time",20)
                            try:
                                new_delay = self.read(i,"return_delay_time")
                                sys.stderr.write("usb2ax: INFO: Servo %d return delay set to %d to make compatible with sync_read\n" % (i, new_delay) )
                            except ReadError, e:
                                sys.stderr.write("usb2ax: WARNING: Failed to fix return delay time for servo %d\n" % i )
                                self.sync_read_ok = False

                        else:
                            sys.stderr.write("usb2ax: Delay time is %d -- you cannot use sync_read\n" % delay )
                            sys.stderr.write("usb2ax: To fix this automatically call initialize with fix_sync_read_delay=True\n" )
                            self.sync_read_ok = False

                except ReadError, e:
                    sys.stderr.write("usb2ax: WARNING: Failed to establish return delay time for servo %d\n" % i )
            except ReadError, e:
                #Servo not connected, do nothing
                pass

        if no_devices_connected:
            sys.stderr.write ("usb2ax: WARNING: Cannot see any devices on the bus!\n" )


        try:
            usb2ax_model_no = _read(0xFD, 0x00, 2)
            usb2ax_firmware_version = _read(0xFD, 0x02, 1)

            sys.stderr.write( """usb2ax: Model no.       : %d
usb2ax: Firmware version: %d
usb2ax: Success!
""" % ( usb2ax_model_no, usb2ax_firmware_version ) )
        except ReadError, e:
            sys.stderr.write( """USB2AX: Could not read model and firmare information, this could be a problem...\n""" )
            sys.stderr.write( "Error number %d\n" % e.error_id )

  
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        dxl_terminate()

    def write(self,servo_id,parameter,value):
        """
        Write to a servos control memory.

        The online documentation lists the supported parameters.

        Call like

        write(1,"goal_position",512)

        To set the target position of the servo with bus ID 1
        to 512 (i.e. the middle).
        """

        if parameter not in MMAP.keys():
            print "Could not write unknown parameter %s" % parameter
            raise UnknownParameterError()

        info = MMAP[parameter]
        if not info[2]:
            print "Parameter %s not writable" % parameter
            raise InvalidWriteParameterError()

        func = dxl_write_byte
        if info[1] == 2:
            func = dxl_write_word

        func(servo_id,info[0],value)
        return

    def read(self,servo_id,parameter):
        """
        Read data from a servo.

        Reads the parameter given from the servo with bus ID servo_id.

        If there is an error, this will raise ReadError. 
        """
        if parameter not in MMAP.keys():
            print "Could not write unknown parameter %s" % parameter
            raise UnknownParameterError()

        info = MMAP[parameter]
        return _read( servo_id, info[0], info[1] )


    def sync_write(self,ids,parameter,values):

        if parameter not in MMAP.keys():
            print "Could not write unknown parameter %s" % parameter
            raise UnknownParameterError()

        info = MMAP[parameter]
        if not info[2]:
            print "Parameter %s not writable" % parameter
            raise InvalidWriteParameterError()

        dxl_set_txpacket_id(254)#Broadcast
        dxl_set_txpacket_instruction(0x83) # Sync write

        param_len = 1 + info[1]

        dxl_set_txpacket_length(param_len*len(ids)+4)

        dxl_set_txpacket_parameter(0,info[0]) 
        dxl_set_txpacket_parameter(1,info[1])

        for i, id in enumerate(ids):
            dxl_set_txpacket_parameter(2+param_len*i,id)
            if info[1] == 2:
                dxl_set_txpacket_parameter(2+param_len*i+1,dxl_get_lowbyte(values[i]))
                dxl_set_txpacket_parameter(2+param_len*i+2,dxl_get_highbyte(values[i]))
            else:
                #Single byte parameter
                dxl_set_txpacket_parameter(2+param_len*i+1,values[i])

        dxl_txrx_packet()
        status = dxl_get_result()

    def sync_read(self,ids,parameter):
        if not self.sync_read_ok:
            raise SyncReadError()

        if parameter not in MMAP.keys():
            print "Could not write unknown parameter %s" % parameter
            raise UnknownParameterError()

        info = MMAP[parameter]

        n_servos = len(ids)

        dxl_set_txpacket_id(253)#USB2AX reserved ID
        dxl_set_txpacket_instruction(0x84) # Sync read
        dxl_set_txpacket_length(n_servos+4)

        dxl_set_txpacket_parameter(0,info[0]) 
        dxl_set_txpacket_parameter(1,info[1])

        for i, id in enumerate(ids):
            dxl_set_txpacket_parameter(2+i,id)

        dxl_txrx_packet()
        status = dxl_get_result()
        if status == COMM_RXSUCCESS:
            check_rx_error()
            if info[1] == 2:
                result = [ dxl_makeword(dxl_get_rxpacket_parameter(2*i),
                    dxl_get_rxpacket_parameter(2*i+1) ) for i in range(n_servos) ]
            else:
                result = [ dxl_get_rxpacket_parameter(i) for i in range(n_servos) ]
        else:
            raise ReadError(status)

        return result
