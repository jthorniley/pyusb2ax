import usb2ax
import time
import math
import sys

with usb2ax.Controller(fix_sync_read_delay = True) as dxl:
    servo_list = dxl.servo_list
    if len(servo_list) == 0:
        raise "Nothing connected..."
        sys.exit()


    print "Servo: \t" + "\t".join( [str(x) for x in servo_list] ) + "\tRead rate (Hz)\tNumber of errors"


    buflen = 1000
    freq_buffer = [0.0] * buflen
    i = 0

    pos_data = [0]*len(servo_list)
    n_read_errors = 0
    try:

        t0 = time.time()
        while True:
            pos = math.sin(t0*math.pi)*50.0 
            pos = int(512+pos)
            for servo in servo_list:
                dxl.write(servo, "goal_position", pos, register=True )

            dxl.action()

            done = False
            while not done:
                try:
                    pos_data = dxl.sync_read(servo_list,"present_position")
                    done = True
                except usb2ax.ReadError, e:
                    n_read_errors += 1
            t1 = time.time()
            freq = 1.0/(t1-t0)
            t0 = t1
            freq_buffer[i] = freq
            mean_freq = sum(freq_buffer)/float(buflen)
            i += 1
            i = i % buflen

            pos_string = "".join(["{:<8d}".format(x) for x in pos_data])
            sys.stdout.write("\r\t{}{:<8.2f}\t{:<8d}".format(pos_string, mean_freq, n_read_errors) )
            sys.stdout.flush()


    except KeyboardInterrupt, e:
        print ""
