#!/usr/bin/python

import threading
import time
import socket
import sys
import time
import sys
import RPi.GPIO as GPIO
from picamera.array import PiRGBArray
from picamera import PiCamera


import msvcrt

# def kbfunc():
#    x = msvcrt.kbhit()
#    if x:
#     ret = ord(msvcrt.getch())
#     print "type:",ret
#    else:
#       ret = 0
#    return ret

flagdanger=False

sys.path.append('/usr/local/lib/python2.7/site-packages')

import cv2
import numpy as np

camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 50
camera.vflip = True

rawCapture = PiRGBArray(camera, size=(640, 480))


MYPORT = 50000
msgDict = {}

speed=10
distance=1000
arrival_time=1000000
reached_int=1
crossed_int=0
at_int=0
closest=0

debugfile=open("debugv1.txt","a")
# initialize the camera and grab a reference to the raw camera capture

foundsign=False
closetosign=False
# allow the camera to warmup
time.sleep(0.1)

GPIO.setwarnings(False)

left_motor_1 = 5
left_motor_2 = 6
right_motor_1 = 13
right_motor_2 = 12
# speed = 37
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
    while True:
        time.sleep(0.05)
        time.sleep(2)
        if foundsign==True:
            udpclient("danger")
        else:
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
    global closest
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind(('',MYPORT))
    #server_address = (car1host, car1port)
    # print >>sys.stderr, 'starting up on %s port %s' % server_address
    #sock.bind(server_address)
    while True:
        # print >>sys.stderr, '\nwaiting to receive message'
        data, address = sock.recvfrom(4096)

        #print >>sys.stderr, 'received %s bytes from %s' % (len(data), address)
        print >>sys.stderr, "receive:"+data

        if data:
            valueList=data.split("|")
            car=valueList[0]
            msgDict[car]=data;
            closest_car=""
            closest_arrival=999999999999
            closest_cross=0
            closest_zreach=0
            for myMsg in msgDict:
                # print myMsg+":"+msgDict[myMsg]
                values=msgDict[myMsg].split("|")
                zcar=values[0]
                zarrival=float(values[1])
                zcross=int(values[3])
                zreach=int(values[2])
                if zreach==1 and zcross==0 and zarrival<closest_arrival:
                    closest_car=zcar
                    closest_arrival=zarrival
                    closest_cross=zcross
                    closest_reach=zreach
            if closest_car!=car_ID:
                # print "I am not closest car.The closest is:"+closest_car
                closest=0
            else:
                # print "I am the closest :"+closest_car
                closest=1


def udpclient(message):
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #server_address = (car2host, car2port)
    sock.bind(('', 0))
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    msg=car_ID+"|"+str(arrival_time)+"|"+str(reached_int)+"|"+str(crossed_int)+"|"+message

    try:
        # Send data
        print "%s: %s" % ("udpclient", time.ctime(time.time()))
        print >>sys.stderr, 'sending "%s"' % msg
        #sent = sock.sendto(msg, server_address)
        sock.sendto(msg, ('<broadcast>', MYPORT))
        time.sleep(1) #very important. without it can
    finally:
        print >>sys.stderr, 'closing socket'
        sock.close()


valueinmain="main"

if len(sys.argv)!=2:
    print sys.argv[0], "car_ID"
    sys.exit()

car_ID=sys.argv[1]
if car_ID == "car2":
    speed=20
if car_ID == "car3":
    speed=30

udpServerT = udpServerThread(1, "UDP Server")
udpServerT.setDaemon(True)  #when main exit, this thread exit
udpServerT.start()

udpClientT = udpClientThread(2, "UDP Client ")
udpClientT.setDaemon(True)  #when main exit, this thread exit
udpClientT.start()

key=0

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
                  width=rect[2][0]-rect[1][0]
                  height=rect[0][1]-rect[1][1]
                  distance=width*10000
                  print "%dpx %dpx" % (width,height)
        #cv2.imshow("Frame", blur)
        #cv2.imshow('thresh',thresh2)
        time.sleep(0.025)


	# clear the stream in preparation for the next frame
        rawCapture.truncate(0)

        ts = time.time()
        arrival_time=ts+(distance/speed)

        if width > 200:
            at_int=1

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
            crossed_int = 1

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

        if closest==0 and at_int==1 and crossed_int==0:
            # print "stop"+" closest:"+str(closest)+" at_int:"+str(at_int)
            # time.sleep(1)
            while True:
                left_1.start(0)
                left_2.start(0)
                right_1.start(0)
                right_2.start(0)



print "Exiting Main Thread"
