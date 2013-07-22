# some functions for dealing with fiducials
# a useful abstraction...

import math

def get_center(fiducial):
    xs = fiducial[1:8:2] # slice x coordinates
    ys = fiducial[2:9:2] # slice y coordinates
    center = [ (sum(xs) / len(xs)), (sum(ys) / len(ys)) ]
    return center

def get_orientation(fiducial):
    orientation = fiducial[14] * (math.pi / 180)
    return orientation

def get_fiducial_name(fiducial, path):
    index = int(fiducial[15])
    length = int(fiducial[16])
    name = path[index:(length + index) - 1]
    return name

def get_scale(fiducial):
    scale = float(fiducial[11])
    return scale
