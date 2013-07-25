#!/usr/bin/python

# simple code to operate multiple spiders
import array
import time
import math
import sys
import os
import serial

# import Roborealm API Classes and fiducial functions
from RR_API import RR_API
import fiducials as fid

# instantiate RR_API class and connet to the API
# running on local computer
rr = RR_API()
rr.Connect("localhost")

# this needs to be changed to the correct COM port
# if it changes
PORT = 'COM6'
BAUD_RATE = 38400 # optimized for the panstamp

# create serial object to communicate with transmitter
ser = serial.Serial(PORT, BAUD_RATE)

while True:
    try:
        # set reference coordinates
        x_r = 100
        y_r = 100
        # get FIDUCIALS and FIDUCIALS_PATH variables from RR_API
        fiducials = rr.GetFiducials()
        fiducialsPath = rr.GetFiducialsPath()

        # get orientation, position and name from every fiducial
        for key in fiducials.iterkeys():
            name = fid.get_fiducial_name(fiducials[key], fiducialsPath)

            if name == 'attic.gif':
                center_2 = fid.get_center(fiducials[key])
                x_2 = int(round(center_2[0]))
                y_2 = int(round(center_2[1]))
            elif name == 'balcony.gif':
                center = fid.get_center(fiducials[key])
                x = int(round(center[0]))
                y = int(round(center[1]))
                orientation = fid.get_orientation(fiducials[key])

        print "spider number: {0}".format(spider)
        print "x: {0}, y: {1}, angle: {2}".format(x, y, orientation)
        print "x_2: {0}, y_2: {1}".format(x_2, y_2)
        ser.write("-./{0},{1},{2},{3},{4},{5}".format(spider, y_r, x_r,
                                                      y, x, (orientation * 1000),
                                                      y_2, x_2))
        time.sleep(.1)

    except KeyError:
        pass

    except KeyboardInterrupt:
        print "all done"
        break

# close handle to transmitter object.
ser.close()
