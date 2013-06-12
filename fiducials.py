# code for tracking fiducials and trasmitting to networked
# XBees
#!/usr/bin/python

import socket
import re
import array
import time
import math

from xbee import XBee, ZigBee
import serial

from collections import defaultdict

TIMEOUT = 30
SERVER_PORT = 6060

VarParReq=re.compile('<response><[^>]+>([^<]*)</[^>]+></response>')
HitWidReq=re.compile('<response><width>([^<]*)</width><height>([^<]*)</height></response>')

class RR_API:
  def __init__(self):
    #create an INET, STREAMing socket
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #only wait TIMEOUT seconds for any request
    self.sock.settimeout(TIMEOUT)

  def escape(self, str):
    str = str.replace("&", "&amp;")
    str = str.replace('"', "&quot;")
    str = str.replace("<", "&lt;")
    str = str.replace(">", "&gt;")
    return str

  def write(self, msg, msgLen):
    totalsent = 0
    # keep sending while there is more data to send
    while totalsent < msgLen:
      sent = self.sock.send(msg[totalsent:msgLen])
      if sent == 0:
        raise RuntimeError, "socket connection broken"
      totalsent = totalsent + sent

  def read(self, msgLen):
    msg = ""
    max = 0
    while (max < msgLen):
      chunk = self.sock.recv(msgLen-max)
      if chunk == '':
          raise RuntimeError, "socket connection broken"
      msg = msg + chunk
      max = max + len(chunk)
    return msg

  # Buffered socket image read. Since we don't know how much data was read from a
  # previous socket operation we have to add in any previously read information
  # that may still be in our buffer. We detect the end of XML messages by the
  # </response> tag but this may require reading in part of the image data that
  # follows a message. Thus when reading the image data we have to move previously
  # read data to the front of the buffer and continuing reading in the
  # complete image size from that point.
  def readMessage(self):
    msg = ""
    while True:
      byte = self.sock.recv(1)
      if byte == '':
        raise RuntimeError, "socket connection broken"
      msg = msg + byte
      if (msg[-11:] == "</response>"):
        return msg

  # Initiates a socket connection to the RoboRealm server
  def Connect(self, hostname):
    self.sock.connect((hostname, SERVER_PORT))

  def GetDimension(self):
    self.sock.send('<request><get_dimension/></request>')
    data = self.readMessage()
    m = HitWidReq.match(data)
    if m:
      width = m.group(1)
      height = m.group(2)
    else:
      width = 0
      height = 0
    return width, height

  # close the socket handle
  def close(self):
    self.sock.close()

  # Returns the current processed image.
  def GetImage(self, name):
    self.sock.send("<request><get_image>" + name + "</get_image></request>")
    data = self.readMessage()
    m = re.match('<response><length>([^<]*)</length><width>([^<]*)</width><height>([^<]*)</height></response>', data)
    if m:
      len = int(m.group(1))
      width = int(m.group(2))
      height = int(m.group(3))
      newPixels = self.read(len)
    else:
      newPixels = array.array('B', [0 for i in range(1)])
      width = 0
      height = 0
    return newPixels, width, height

  # Sets the current source image.
  def SetImage(self, name, pixels, width, height):
    self.sock.send("<request><set_image><source>"+name+"</source><width>"+str(width)+"</width><height>"+str(height)+"</height></set_image></request>")
    self.write(pixels, width*height*3)
    if (self.readMessage() == "<response>ok</response>"):
      return 1
    else:
      return 0

  # Returns the value of the specified variable.
  def GetVariable(self, name):
    self.sock.send("<request><get_variable>"+str(name)+"</get_variable></request>")
    data = self.readMessage()
    m = VarParReq.match(data)
    if m:
      value = m.group(1)
    else:
      value = ""
    return value

  # Returns all variables in RoboRealm as a dict
  def GetAllVariables(self):
    self.sock.send("<request><get_all_variables></get_all_variables></request>")
    response = self.readMessage()
    response = re.sub("(<response>)|(</response>)", "", response)
    values = re.findall("<(?P<VAR>.+)>(.+)</(?P=VAR)>", response)
    data = dict({})
    for key, value in values:
      data[key] = value
    return data

  # Sets the value of the specified variable.
  def SetVariable(self, name, value):
    self.sock.send("<request><set_variable><name>"+self.escape(str(name))+"</name><value>"+self.escape(str(value))+"</value></set_variable></request>")
    if (self.readMessage() == "<response>ok</response>"):
      return 1
    else:
      return 0

  # Deletes the specified variable
  def DeleteVariable(self, name):
    self.sock.send("<request><delete_variable>"+self.escape(str(name))+"</delete_variable></request>")
    if (self.readMessage() == "<response>ok</response>"):
      return 1
    else:
      return 0

  # Executes the provided image processing pipeline
  def Execute(self, source):
    self.sock.send("<request><execute>"+self.escape(str(source))+"</execute></request>")
    if (self.readMessage() == "<response>ok</response>"):
      return 1
    else:
      return 0

  # Executes the provided .robo file. Note that the file needs to be on the machine
  # running RoboRealm. This is similar to pressing the 'open program' button in the
  # main RoboRealm dialog.
  def LoadProgram(self, filename):
    self.sock.send("<request><load_program>"+self.escape(str(filename))+"</load_program></request>")
    if (self.readMessage() == "<response>ok</response>"):
      return 1
    else:
      return 0

  # Loads an image into RoboRealm. Note that the image needs to exist
  # on the machine running RoboRealm. The image format must be one that
  # RoboRealm using the freeimage.dll component supports. This includes
  # gif, pgm, ppm, jpg, png, bmp, and tiff. This is
  # similar to pressing the 'load image' button in the main RoboRealm
  # dialog.
  def LoadImage(self, name, filename):
    self.sock.send("<request><load_image><name>"+self.escape(str(name))+"</name><filename>"+self.escape(str(filename))+"</filename></load_image></request>")
    if (self.readMessage() == "<response>ok</response>"):
      return 1
    else:
      return 0

  # Saves the specified image in RoboRealm to disk. Note that the filename is relative
  # to the machine that is running RoboRealm. The image format must be one that
  # RoboRealm using the freeimage.dll component supports. This includes
  # gif, pgm, ppm, jpg, png, bmp, and tiff. This is
  # similar to pressing the 'save image' button in the main RoboRealm
  # dialog.
  def SaveImage(self, filename):
    self.sock.send("<request><save_image><filename>"+self.escape(str(filename))+"</filename></save_image></request>")
    if (self.readMessage() == "<response>ok</response>"):
      return 1
    else:
      return 0

  # Sets the current camera driver. This can be used to change the current viewing camera
  # to another camera installed on the same machine. Note that this is a small delay
  # when switching between cameras. The specified name needs only to partially match
  # the camera driver name seen in the dropdown picklist in the RoboRealm options dialog.
  # For example, specifying "Logitech" will select any installed Logitech camera including
  # "Logitech QuickCam PTZ".
  def SetCamera(self, name):
    self.sock.send("<request><set_camera>"+self.escape(name)+"</set_camera></request>")
    if (self.readMessage() == "<response>ok</response>"):
      return 1
    else:
      return 0

  # This routine provides a way to stop processing incoming video. Some image processing
  # tasks can be very CPU intensive and you may only want to enable processing when
  # required but otherwise not process any incoming images to release the CPU for other
  # tasks. The run mode can also be used to processing individual frames or only run
  # the image processing pipeline for a short period. This is similar to pressing the
  # "run" button in the main RoboRealm dialog.
  def Run(self, mode):
    self.sock.send("<request><run>"+self.escape(mode)+"</run></request>")
    if (self.readMessage() == "<response>ok</response>"):
      return 1
    else:
      return 0

  # There is often a need to pause your own Robot Controller program to wait for
  # RoboRealm to complete its task. The eaisest way to accomplish this is to wait
  # on a specific variable that is set to a specific value by RoboRealm. Using the
  # waitVariable routine you can pause processing and then continue when a variable
  # changes within RoboRealm.
  def WaitVariable(self, name, value, timeout):
    self.sock.send("<request><wait_variable><name>"+self.escape(name)+"</name><value>"+self.escape(value)+"</value><timeout>"+str(timeout)+"</timeout></request>")
    if (self.readMessage() == "<response>ok</response>"):
      return 1
    else:
      return 0

  # If you are rapdily grabbing images you will need to wait inbetween each
  # get_image for a new image to be grabbed from the video camera. The wait_image
  # request ensures that a new image is available to grab. Without this routine
  # you may be grabbing the same image more than once.
  def WaitImage(self, timeout):
    self.sock.send("<request><wait_image><timeout>"+str(timeout)+"</timeout></wait_image></request>")
    if (self.readMessage() == "<response>ok</response>"):
      return 1
    else:
      return 0

  # Mainly used for reference or degugging. Prints out all the current variables from
  # RoboRealm as it appears in an XML string.
  def ReadAll(self):
    self.sock.send("<request><get_all_variables></get_all_variables></request>")
    data=self.readMessage()
    print data

  #Gets the Value of the Specified Parameter (as apposed to a variable value)
  def GetParamVal(self, modname, modindex, paramname):
    self.sock.send("<request><set_parameter><module>" + self.escape(str(modname)) + "</module><module_number>" + self.escape(str(modindex)) + "</module_number><name>" + self.escape(str(paramname)) + "</name></set_parameter></request>")
    data=self.readMessage()
    m=VarParReq.match(data)
    if m:
      value=m.group(1)
    else:
      value=""
    return value

  #Sets the Value of the Specified Parameter
  def SetParamVal(self,modname,modindex,paramname,paramvalue):
    self.sock.send("<request><set_parameter><module>" + self.escape(str(modname)) + "</module><module_number>" + self.escape(str(modindex)) + "</module_number><name>" + self.escape(str(paramname)) + "</name><value>" + self.escape(str(paramvalue)) + "</value></set_parameter></request>")
    if (self.readMessage() == "<response>ok</response>"):
      return 1
    else:
      return 0

rr = RR_API()
rr.Connect("localhost")

# set up xbee for communication
PORT = '/dev/tty.usbserial-A601ETWD'
BAUD_RATE = 9600

ser = serial.Serial( PORT, BAUD_RATE )
xbee = ZigBee( ser, escaped=True )

DEST_ADDR_LONG = "\x00\x13\xA2\x00\x40\xAA\x18\xD5"
DEST_ADDR = "\xFF\xFE"

print "running test program"
testout = open( "data", 'w')

array = [1, 2, 3, 4]

while True:
    try:
        data = rr.GetAllVariables()

        # grab all the information we can get and make it useful
        fiducials = data['FIDUCIALS'].split(',')
        fiducials = map( float, fiducials )

        # 17 values per fiducial, see roborealm documentation for
        # information on the contents of particular indices
        print "this many fiducials: {0}\n".format(len( fiducials ) / 17)

        fiducialMatrix = [[fiducials[j] for j in range( (i*17), (i*17) + 17 )]
                        for i in range(0, (len(fiducials) /17))]

        # create dict of all the fiducials being tracked
        # keys in the dict are referencds like FID0..FID(n)
        fiducialDict = {}

        for i in range(0, (len(fiducials) / 17)):
            testout.write( "\nfiducial number %d\n" % int(i + 1) )
            fiducialDict['FID{0}'.format(i + 1)] = fiducialMatrix[i]
            for j in range( (i * 17), (i * 17) + 16 ):
                testout.write( "{0}".format(fiducials[j]) )
                testout.write( "\n" )

        # calculate coordinate pairs for centers
        centers = {}
        sizes = {} 

        for key in sorted( fiducialDict.iterkeys() ):

            # get all the x coordinates and all the y coordinates
            xs = fiducialDict[key][1:8:2]
            ys = fiducialDict[key][2:9:2]
            print "orientation z: {0}".format(fiducialDict[key][14])
            centers[key] = [ (sum(xs) / len(xs)), (sum(ys) / len(ys)) ]
            # get all the sizes of the fiducials
            sizes[key] = fiducialDict[key][11]

        # return which key is the spider, hopefully the largest marker
        spider = max(sizes.iterkeys(), key=lambda k: sizes[k])
        print "the spider: {0}".format(spider)

        for key in sorted( centers.iterkeys() ):
            print "%s" % key
            # send the x and y to the receiving xbee
            print "sending coordinates"
            simplex = int(round(centers[key][0]))
            simpley = int(round(centers[key][1]))

            print "({0}, {1})".format(simplex, simpley)

            orientation = fiducialDict[key][14] * (math.pi / 180)
            print "orientation z (rad): {0}".format(orientation)

            xbee.tx(dest_addr_long=DEST_ADDR_LONG, dest_addr=DEST_ADDR,
                    data="-{0},{1},{2},{3},{4}".format(640,480,
                        simplex,simpley,orientation))

            time.sleep(.1)
            print "\n"

    except KeyError:
        print "no fiducial in vision"
        pass
    except KeyboardInterrupt:
        break
        print "all done"

testout.close()
ser.close()
