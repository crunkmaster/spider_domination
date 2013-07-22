#!/usr/bin/python

import array
import time
import math
import sys
import os
import serial

from RR_API import RR_API
import fiducials as fid

rr = RR_API()
rr.Connect("localhost")

# this needs to be changed to the correct COM port
# if it changes
PORT = 'COM6'
BAUD_RATE = 38400

ser = serial.Serial(PORT, BAUD_RATE)

while True:
    try:
        # get the fiducials from RR_API
        x_r = 100
        y_r = 100
        data = rr.GetAllVariables()
        fiducials = rr.GetFiducials()
        fiducialsPath = rr.GetFiducialsPath()

        for key in fiducials.iterkeys():
            orientation = fid.get_orientation(fiducials[key])
            center = fid.get_center(fiducials[key])
            x = int(round(center[0]))
            y = int(round(center[1]))
            name = fid.get_fiducial_name(fiducials[key], fiducialsPath)

            if name == 'balcony.gif':
                spider = 5
                x_r = 240
                y_r = 50
            elif name == 'garden.gif':
                spider = 6
                x_r = 235
                y_r = 180
            elif name == 'bathroom.gif':
                spider = 7
                x_r = 60
                y_r = 40
            elif name == 'hallway.gif':
                spider = 8
                x_r = 70
                y_r = 180

            print "spider number: {0}".format(spider)
            print "x: {0}, y: {1}, angle: {2}".format(x, y, orientation)
            ser.write("-./{0},{1},{2},{3},{4},{5}".format(spider, y_r, x_r,
                                                          y, x, (orientation * 1000)))
            time.sleep(.1)

    except KeyError:
        pass

    except KeyboardInterrupt:
        print "all done"
        break

ser.close()
