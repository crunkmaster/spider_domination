import array
import time
import math

import os
import serial

from collections import defaultdict
from RR_API import RR_API

rr = RR_API()
rr.Connect("localhost")

# set up RFbee for communication
PORT = 'COM3'
BAUD_RATE = 9600

ser = serial.Serial( PORT, BAUD_RATE )

while True:
    try:
        data = rr.GetAllVariables()

        # grab all the information we can get and make it useful
        fiducials = data['FIDUCIALS'].split(',')
        fiducials = map( float, fiducials )
    
        # 17 values per fiducial, see roborealm documentation for
        # information on the contents of particular indices

        fiducialMatrix = [[fiducials[j] for j in range( (i*17), (i*17) + 17 )]
                        for i in range(0, (len(fiducials) /17))]

        # create dict of all the fiducials being tracked
        # keys in the dict are referencds like FID0..FID(n)
        fiducialDict = {}

        for i in range(0, (len(fiducials) / 17)):
            fiducialDict['FID{0}'.format(i + 1)] = fiducialMatrix[i]

        # calculate coordinate pairs for centers
        centers = {}
        sizes = {} 

        for key in sorted( fiducialDict.iterkeys() ):

            # get all the x coordinates and all the y coordinates
            xs = fiducialDict[key][1:8:2]
            ys = fiducialDict[key][2:9:2]
            centers[key] = [ (sum(xs) / len(xs)), (sum(ys) / len(ys)) ]
            # get all the sizes of the fiducials
            sizes[key] = fiducialDict[key][11]

        # return which key is the spider, hopefully the largest marker
        spider = max(sizes.iterkeys(), key=lambda k: sizes[k])

        for key in sorted( centers.iterkeys() ):
            # send the x and y to the receiving xbee
            simplex = int(round(centers[key][1]))
            simpley = int(round(centers[key][0]))
    
            orientation = fiducialDict[key][14] * (math.pi / 180)
            print orientation
            testout.write("orientation: {0}\n".format(orientation))
            
            ser.write("{0},{1},{2},{3},{4}".format(100, 100, 
            	simplex, simpley, (10000 * orientation)))
            time.sleep(.1)

    except KeyError:
        os.system('cls')
        print "no fiducial in vision"
        time.sleep(1)
        os.system('cls')
        pass
    except KeyboardInterrupt:
        print "all done"
        break
