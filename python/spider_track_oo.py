#!/usr/bin/python

import array
import time
import math
import os
import serial

from RR_API import RR_API
from fiducials import Fiducials

rr = RR_API()
rr.Connect("localhost")

PORT = 'COM6'
BAUD_RATE = 38400

ser = serial.Serial(PORT, BAUD_RATE)

while True:
    data = rr.GetFiducials()
    Fiducials.path = rr.GetFiducialsPath()
    
    for key in data.iterkeys():
        name = key
        
    
