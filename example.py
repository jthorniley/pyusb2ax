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

print "Servo: \t" + "\t".join( sys.argv[1:] ) + "\tRead freq (Hz)"

usb2ax.initialize()

t0 = time.time()

buflen = 500
freq_buffer = [0.0] * buflen
i = 0

while True:
    pos = math.sin(t0*math.pi)*50.0 
    pos = int(512+pos)
    usb2ax.sync_write(servo_list,"goal_position",[pos]*len(servo_list))

    pos_data = usb2ax.sync_read(servo_list,"goal_position")

    t1 = time.time()
    freq = 1.0/(t1-t0)
    t0 = t1
    freq_buffer[i] = freq
    mean_freq = sum(freq_buffer)/float(buflen)
    i += 1
    i = i % buflen

    pos_string = "\t".join(["%s" % x for x in pos_data])
    sys.stdout.write("\r\t%s\t%.2f" % (pos_string, mean_freq) )
    sys.stdout.flush()

