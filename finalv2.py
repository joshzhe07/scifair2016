#!/usr/bin/python

import threading
import time
import socket
import sys
import RPi.GPIO as GPIO
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import sys

flagdanger=False
foundsign=False
closetosign=False

sys.path.append('/usr/local/lib/python2.7/site-packages')

import cv2
import numpy as np

debugfile=open("/tmp/debugcv.txt","a")
# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 50
camera.vflip = True

rawCapture = PiRGBArray(camera, size=(640, 480))


# allow the camera to warmup
time.sleep(0.1)

class udpClientThread (threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
    def run(self):
        # print "Starting " + self.name
        sendMsg(self.name)

def sendMsg(threadName):
    global flagdanger
    global closetosign
    while True:
        time.sleep(0.05)
        if foundsign==True:
            udpclient("danger")
        if foundsign==False:
            udpclient("safe")




class udpServerThread (threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
    def run(self):
        # print "Starting " + self.name
        udpserver(self.name)

def udpserver(threadName):
    # Create a TCP/IP socket
    global flagdanger
    global closetosign
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = (car1host, car1port)
    print >>sys.stderr, 'starting up on %s port %s' % server_address
    sock.bind(server_address)
    while True:
        #print >>sys.stderr, '\nwaiting to receive message'
        data, address = sock.recvfrom(4096)

        #print >>sys.stderr, 'received %s bytes from %s' % (len(data), address)
        print >>sys.stderr, data

        if data:
            sent = sock.sendto(data, address)
            # print >>sys.stderr, 'sent %s bytes back to %s' % (sent, address)
            # if data=="sendtest":
            #     udpclient("sendtest to another car")
            if data=="danger":
                flagdanger=True
            if data=="safe":
                flagdanger=False
            if data=="close":
                closetosign=True
            if data=="unclose":
                closetosign=False


def udpclient(message):
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = (car2host, car2port)

    try:
        # Send data
        # print "%s: %s" % ("udpclient", time.ctime(time.time()))
        print >>sys.stderr, 'sending "%s"' % message
        sent = sock.sendto(message, server_address)
        # Receive response
        print >>sys.stderr, 'waiting to receive'
        data, server = sock.recvfrom(4096)
        print >>sys.stderr, 'received "%s"' % data

    finally:
        # print >>sys.stderr, 'closing socket'
        sock.close()


valueinmain="main"

if len(sys.argv)!=5:
    print sys.argv[0], "host1 port1 host2 port2"
    sys.exit()

car1host,car1port=sys.argv[1],int(sys.argv[2])
car2host,car2port=sys.argv[3],int(sys.argv[4])

udpServerT = udpServerThread(1, "UDP Server")
udpServerT.setDaemon(True)  #when main exit, this thread exit
udpServerT.start()

#udpClientT = udpClientThread(2, "UDP Client ")
#udpClientT.setDaemon(True)  #when main exit, this thread exit
#udpClientT.start()

GPIO.setwarnings(False)

left_motor_1 = 5
left_motor_2 = 6
right_motor_1 = 13
right_motor_2 = 12
speed = 37
# speed = 30
READR = 17
READL = 27

GPIO.setmode(GPIO.BCM)
GPIO.setup(right_motor_1, GPIO.OUT)
GPIO.setup(right_motor_2, GPIO.OUT)
GPIO.setup(left_motor_1, GPIO.OUT)
GPIO.setup(left_motor_2, GPIO.OUT)


GPIO.setup (READR,GPIO.IN)
GPIO.setup (READL,GPIO.IN)


left_1 = GPIO.PWM(left_motor_1,100)
left_2 = GPIO.PWM(left_motor_2,100)
right_1 = GPIO.PWM(right_motor_1,100)
right_2 = GPIO.PWM(right_motor_2,100)

width=0
height=0

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	# grab the raw NumPy array representing the image, then initialize the timestamp
	# and occupied/unoccupied text
        image = frame.array

        blur = cv2.blur(image, (3,3))

        lower = np.array([17,1,100],dtype="uint8")
        upper = np.array([200,59,225], dtype="uint8")

        thresh = cv2.inRange(blur, lower, upper)
        thresh = cv2.GaussianBlur(thresh, (3, 3), 0)
        thresh2 = thresh.copy()

        # find contours in the threshold image
        #image, contours,hierarchy = cv2.findContours(thresh,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
        image, contours,hierarchy = cv2.findContours(thresh,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        # finding contour with maximum area and store it as best_cnt
        max_area = 0
        best_cnt = 1
        focallen=1.23
        height=0
        width=0
        if len(contours) > 0:
	          cnt = sorted(contours, key = cv2.contourArea, reverse = True)[0]
                  rect = np.int32(cv2.boxPoints(cv2.minAreaRect(cnt)))
                  cv2.drawContours(blur, [rect], -1, (0, 255, 0), 2)
                  #print "rect",rect
                  #print "%dpx %.2fft" % (rect[1][0],rect[1][0]/focallen)
                  #print "%dpx %dpx" % (rect[1][0],rect[1][1])
                  width=rect[2][0]-rect[1][0]
                  height=rect[0][1]-rect[1][1]
                  print "%dpx %dpx" % (width,height)
                #   debugfile.write(str(width)+';'+str(height) + "\n")

                  if height>100:
                      print "car1 found the stop sign"
                      foundsign=True
                #   cv2.putText(blur,"%dpx %.2fft" % (rect[1][0],rect[1][0]/focallen), (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,0,255),2)
        #cv2.imshow("Frame", blur)
        #cv2.imshow('thresh',thresh2)
        time.sleep(0.025)
        #print "best_cnt",best_cnt,"area",max_area
        # key = cv2.waitKey(1) & 0xFF

	# clear the stream in preparation for the next frame
        rawCapture.truncate(0)

	# if the `q` key was pressed, break from the loop
        # if key == ord("q"):
        # 	break

    # print "%s: %s" % (valueinmain, time.ctime(time.time()))
    #time.sleep(1)  # Delay for 1 minute (60 seconds)

        if GPIO.input(READR) == 0 and GPIO.input(READL) == 0:
            left_1.start(speed)
            left_2.start(speed*0)
            right_1.start(speed)
            right_2.start(speed*0)

        if GPIO.input(READR) == 1 and GPIO.input(READL) == 1:
            left_1.start(speed)
            left_2.start(speed*0)
            right_1.start(speed)
            right_2.start(speed*0)
            foundsign=False
            print "car1 has crossed the intersection"

        if GPIO.input(READR) == 0 and GPIO.input(READL) == 1:
            left_1.start(speed*0.5)
            left_2.start(speed*0)
            right_1.start(speed*0)
            right_2.start(speed*0)

        if GPIO.input(READR) == 1 and GPIO.input(READL) == 0:
            left_1.start(speed*0)
            left_2.start(speed*0)
            right_1.start(speed*0.5)
            right_2.start(speed*0)


        #if  height>200:
        #    closetosign=True
        # key = cv2.waitKey(1) & 0xFF

        print "closetosign",closetosign

        # # if key==ord("c"):
        #    closetosign=True
        #
        #
        # if key==ord("f"):
        #    closetosign=False

        if closetosign==True:
            height=210
            print "height is changed"
        if closetosign==False:
            height=190

        if height>200:
            print "car2 has reached the intersection"
            while flagdanger==True:
                print "stop"," ",closetosign," ",flagdanger
                left_1.start(0)
                left_2.start(0)
                right_1.start(0)
                right_2.start(0)


print "Exiting Main Thread"
