#!/usr/bin/python

# the program to connect roborealm and the blimp
import array
import time
import math
import os
import serial

from collections import defaultdict
from RR_API import RR_API
import fiducials as fid

rr = RR_API()
rr.Connect("localhost")

# this needs to be changed to the correct COM port
PORT = 'COM6'
BAUD_RATE = 38400

ser = serial.Serial(PORT, BAUD_RATE)

while True:
    try:
        # get all variables from RR_API
        x_r = 100
        y_r = 100
        data = rr.GetAllVariables()
        fiducials = fid.get_fiducials(data)
        
        for key in sorted(fiducials.iterkeys()):
            orientation = fid.get_orientation(fiducials[key])
            center = fid.get_center(fiducials[key])
            simplex = int(round(center[0]))
            simpley = int(round(center[1]))
            name = fid.get_fiducial_name(fiducials[key], data)

            if name == 'arrow.gif':
                spider = 5
            elif name == 'bathroom.gif':
                spider = 7
            elif name == 'hallway.gif':
                spider = 8
            elif name == 'garden.gif':
                spider = 6

            print "spider number: {0}".format(spider)
            print "x: {0}, y: {1}, angle: {2}".format(simplex, simpley, orientation)
            ser.write("-./{0},{1},{2},{3},{4},{5}".format(spider, x_r, y_r,
                            simpley, simplex, (orientation * 1000)))
            time.sleep(.1)

    except KeyError:
        pass

    except KeyboardInterrupt:
        print "all done"
        break

ser.close()
