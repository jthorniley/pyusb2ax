import usb2ax
import time
import math
import sys

if len(sys.argv) == 1:
    print """Usage: python example.py [id1] [id2] ...
E.g. python example.py 1 2 will move servos
1 and 2 and read back the positions information
"""
    sys.exit()

servo_list = [int(x) for x in sys.argv[1:]]

try:
    usb2ax.initialize()

    print "Servo: \t" + "\t".join( sys.argv[1:] ) + "\tRead freq (Hz)"

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
            usb2ax.sync_write(servo_list,"goal_position",[pos]*len(servo_list))

            #pos_data = [usb2ax.read(1,"present_position")]
            done = False
            while not done:
                try:
                    pos_data = usb2ax.sync_read(servo_list,"present_position")
                    done = True
                except usb2ax.ReadError, e:
                    #print "Read error"
                    n_read_errors += 1
            t1 = time.time()
            freq = 1.0/(t1-t0)
            t0 = t1
            freq_buffer[i] = freq
            mean_freq = sum(freq_buffer)/float(buflen)
            i += 1
            i = i % buflen

            pos_string = "".join(["{:<8d}".format(x) for x in pos_data])
            sys.stdout.write("\r\t{}{:<8.2f}".format(pos_string, mean_freq) )
            sys.stdout.flush()


    except KeyboardInterrupt, e:
        print ""
        print "Number of read errors: %d" % n_read_errors
finally:
    usb2ax.terminate()

