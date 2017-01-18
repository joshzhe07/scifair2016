#!/usr/bin/python

import threading
import time
import socket
import sys
#import RPi.GPIO as GPIO


class udpServerThread (threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
    def run(self):
        print "Starting " + self.name
        udpserver(self.name)

def udpserver(threadName):
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = (car1host, car1port)
    print >>sys.stderr, 'starting up on %s port %s' % server_address
    sock.bind(server_address)
    while True:
        print >>sys.stderr, '\nwaiting to receive message'
        data, address = sock.recvfrom(4096)

        print >>sys.stderr, 'received %s bytes from %s' % (len(data), address)
        print >>sys.stderr, data

        if data:
            sent = sock.sendto(data, address)
            print >>sys.stderr, 'sent %s bytes back to %s' % (sent, address)
            if data=="sendtest":
                udpclient("sendtest to another car")


def udpclient(message):
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = (car2host, car2port)

    try:
        # Send data
        print >>sys.stderr, 'sending "%s"' % message
        sent = sock.sendto(message, server_address)
        # Receive response
        print >>sys.stderr, 'waiting to receive'
        data, server = sock.recvfrom(4096)
        print >>sys.stderr, 'received "%s"' % data

    finally:
        print >>sys.stderr, 'closing socket'
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

# GPIO.setwarnings(False)
#
# left_motor_1 = 6
# left_motor_2 = 5
# right_motor_1 = 12
# right_motor_2 = 13
# speed = 40
# READR = 27
# READL = 17
#
# GPIO.setmode(GPIO.BCM)
# GPIO.setup(right_motor_1, GPIO.OUT)
# GPIO.setup(right_motor_2, GPIO.OUT)
# GPIO.setup(left_motor_1, GPIO.OUT)
# GPIO.setup(left_motor_2, GPIO.OUT)
#
#
# GPIO.setup (READR,GPIO.IN)
# GPIO.setup (READL,GPIO.IN)
#
#
# left_1 = GPIO.PWM(left_motor_1,100)
# left_2 = GPIO.PWM(left_motor_2,100)
# right_1 = GPIO.PWM(right_motor_1,100)
# right_2 = GPIO.PWM(right_motor_2,100)



while True:
    print "%s: %s" % (valueinmain, time.ctime(time.time()))
    time.sleep(1)  # Delay for 1 minute (60 seconds)
    # if GPIO.input(READR) == 0 and GPIO.input(READL) == 0:
    #     left_1.start(speed)
    #     left_2.start(speed*0)
    #     right_1.start(speed)
    #     right_2.start(speed*0)
    #
    # if GPIO.input(READR) == 0 and GPIO.input(READL) == 1:
    #     left_1.start(speed)
    #     left_2.start(speed*0)
    #     right_1.start(speed*0)
    #     right_2.start(speed*0)
    #
    # if GPIO.input(READR) == 1 and GPIO.input(READL) == 0:
    #     left_1.start(speed*0)
    #     left_2.start(speed*0)
    #     right_1.start(speed)
    #     right_2.start(speed*0)


print "Exiting Main Thread"
