
COMM_TXSUCCESS = 0
COMM_RXSUCCESS = 1
COMM_TXFAIL = 2
COMM_RXFAIL = 3
COMM_TXERROR = 4
COMM_RXWAITING = 5
COMM_RXTIMEOUT = 6
COMM_RXCORRUPT = 7
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


def initialize(device_id=0):
    """
    Connect to the USB2AX device.

    Call this before calling anything else.

    The argument goes specifies which ACM device is the
    USB2AX. For example, if the USB2AX is at /dev/ttyACM0,
    call initialize(0) or initialize() (0 is the default
    argument).

    Raises InitError if there was a problem.
    """
    result = dxl_initialize(device_id,1)
    if result == 0:
        raise InitError(device_id)
  
def write(servo_id,parameter,value):
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


def read(servo_id,parameter):
    """
    Attempt to read from a servo.

    Reads the parameter given from the servo with bus ID servo_id.

    If there is an error, this will raise ReadError. 
    """
    if parameter not in MMAP.keys():
        print "Could not write unknown parameter %s" % parameter
        raise UnknownParameterError()

    info = MMAP[parameter]

    func = dxl_read_byte
    if info[1] == 2:
        func = dxl_read_word

    result = func(servo_id, info[0])
    status = dxl_get_result()
    if ( status == COMM_RXSUCCESS):
        return result
    else:
        raise ReadError(status)


def sync_write(ids,parameter,values):

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

def sync_read(ids,parameter):

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
    if ( status == COMM_RXSUCCESS):
        if info[1] == 2:
            return [ dxl_makeword(dxl_get_rxpacket_parameter(2*i),
                dxl_get_rxpacket_parameter(2*i+1) ) for i in range(n_servos) ]
        else:
            return [ dxl_get_rxpacket_parameter(i) for i in range(n_servos) ]

    else:
        raise ReadError(status)
