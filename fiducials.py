#!/usr/bin/python

# import necessary python modules
# nonstandard python modules include: pyserial,
# python-xbee and RR_API.

import array
import time
import math

import os
from xbee import XBee, ZigBee
import serial

from collections import defaultdict
from RR_API import RR_API

# connect to roborealm server running on local machine at
# port 6060.
rr = RR_API()
rr.Connect("localhost")

# set up xbee for communication
# port should be replaced with whatever the COM port the sending
# XBee Receives is.
PORT = 'COM3'
BAUD_RATE = 9600 # the default baud rate for XBee

# connect to the XBee serial port
ser = serial.Serial( PORT, BAUD_RATE )

# instantiate a ZigBee object through which to communicate with
# our XBee
xbee = ZigBee( ser, escaped=True )

# this should be changed to the 64 bit address of the receiving XBee
DEST_ADDR_LONG = "\x00\x13\xA2\x00\x40\xAA\x18\xD5"

# this should be changed to the 16 bit address of the receiving XBee,
# leaving as-is should also work
DEST_ADDR = "\xFF\xFF"

print "running test program"

testout = open( "data", 'w')

while True:
    try:
        # get all variables from rr_api
        data = rr.GetAllVariables()

        # grab all the information we can get and make it useful
        fiducials = data['FIDUCIALS'].split(',')
        fiducials = map( float, fiducials )

        # 17 values per fiducial, see roborealm documentation for
        # information on the contents of particular indices

        # generates a matrix of all the tracked fiducials
        fiducialMatrix = [[fiducials[j] for j in range( (i*17), (i*17) + 17 )]
                        for i in range(0, (len(fiducials) /17))]

        # create dictionary of all the fiducials being tracked
        # keys in the dict are references like fiducialDict['0']..fiducialDict['n']
        # ex: values from the first fiducial are accessed by fiducialDict['0']
        fiducialDict = {}

        for i in range(0, (len(fiducials) / 17)):
            fiducialDict['FID{0}'.format(i + 1)] = fiducialMatrix[i]

        # calculate coordinate pairs for centers
        centers = {}
        sizes = {}

        for key in sorted( fiducialDict.iterkeys() ):

            # get all the x coordinates and all the y coordinates.
            xs = fiducialDict[key][1:8:2]
            ys = fiducialDict[key][2:9:2]
            # the center points are found by getting the average of
            # all four points on the fiducial.
            centers[key] = [ (sum(xs) / len(xs)), (sum(ys) / len(ys)) ]
            # get all the sizes of the fiducials.
            sizes[key] = fiducialDict[key][11]

        # send coordinates of all fiducials to receiving xbee
        for key in sorted( centers.iterkeys() ):

            # send the (rounded)x and y to the receiving xbee
            # we shouldn't need any subpixel values
            simplex = int(round(centers[key][1]))
            simpley = int(round(centers[key][0]))

            # grab orientation and convert to radians.
            orientation = fiducialDict[key][14] * (math.pi / 180)
            print orientation
            # log orientation to file for debugging.
            testout.write("orientation: {0}\n".format(orientation))
            # send information to the specified xbee in the following format:
            # "-{targetx},{targety},{currentx},{currenty},{orientation} "
            # the '-' at the beginning is to simplify parsing on the arduino side.
            # orientation is multiplied by 10000 here and later divided by
            # 10000 and cast by a float to work around problems with
            # parsing floats from serial streams on the arudino.
            xbee.tx(dest_addr_long=DEST_ADDR_LONG, dest_addr=DEST_ADDR,
                    data="-{0},{1},{2},{3},{4}".format(100,100,
                        simplex, simpley, (10000 * orientation)))
            time.sleep(.1)

    # this exception is generally triggered when no fiducials are tracked
    except KeyError:
        # on linux change the system call to 'clear'
        os.system('cls')
        print "no fiducial in vision"
        time.sleep(1)
        os.system('cls')
        pass
    # this exception is thrown when ctrl-c is pressed, and it ends the program
    except KeyboardInterrupt:
        print "all done"
        break

# clean up all files and serial ports.
testout.close()
ser.close()
print "ports closed"
