import serial
import time

PORT = 'COM3'
BAUD_RATE = 9600
ser = serial.Serial(PORT, BAUD_RATE)

testout = open("data", "w")

# log everything to file and add timestamps
while True:
    try:
        ts = time.time()
        output = ser.readline()
        print output
        testout.write("data: {0} time: {1}\n".format(output, ts))
    except KeyboardInterrupt:
        print "all done"
        break
testout.close()
ser.close()
