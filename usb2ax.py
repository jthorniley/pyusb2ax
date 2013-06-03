from dynamixel import *

FRONT_LEG_OFFSET = 0.1

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


def write(servo_id,parameter,value):
    if parameter not in MMAP.keys():
        print "Could not write unknown parameter %s" % parameter
        return

    info = MMAP[parameter]
    if not info[2]:
        print "Parameter %s not writable" % parameter
        return

    func = dxl_write_byte
    if info[1] == 2:
        func = dxl_write_word

    func(servo_id,info[0],value)
    return

class ReadError(Exception):
    def __init__(self,error_id):
        self.error_id = error_id

def read(servo_id,parameter):
    if parameter not in MMAP.keys():
        print "Could not write unknown parameter %s" % parameter
        return

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


    return None

