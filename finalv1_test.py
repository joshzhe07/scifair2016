#!/usr/bin/python

import threading
import time
import socket
import sys
import time
import sys

import msvcrt

def kbfunc():
   x = msvcrt.kbhit()
   if x:
    ret = ord(msvcrt.getch())
    print "type:",ret
   else:
      ret = 0
   return ret

flagdanger=False

sys.path.append('/usr/local/lib/python2.7/site-packages')


debugfile=open("debugv1.txt","a")
# initialize the camera and grab a reference to the raw camera capture

foundsign=False
closetosign=False
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
    while True:
        time.sleep(0.05)
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
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = (car1host, car1port)
    # print >>sys.stderr, 'starting up on %s port %s' % server_address
    sock.bind(server_address)
    while True:
        # print >>sys.stderr, '\nwaiting to receive message'
        data, address = sock.recvfrom(4096)

        print >>sys.stderr, 'received %s bytes from %s' % (len(data), address)
        print >>sys.stderr, data

        if data:
            global flagdanger
            sent = sock.sendto(data, address)
            # print >>sys.stderr, 'sent %s bytes back to %s' % (sent, address)
            # if data=="sendtest":
            #     udpclient("sendtest to another car")
            if data=="danger":
                flagdanger=True
            if data=="safe":
                flagdanger=False


def udpclient(message):
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = (car2host, car2port)

    try:
        # Send data
        print "%s: %s" % ("udpclient", time.ctime(time.time()))
        print >>sys.stderr, 'sending "%s"' % message
        sent = sock.sendto(message, server_address)
        # Receive response
        # print >>sys.stderr, 'waiting to receive'
        # data, server = sock.recvfrom(4096)
        # print >>sys.stderr, 'received "%s"' % data

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

udpClientT = udpClientThread(2, "UDP Client ")
udpClientT.setDaemon(True)  #when main exit, this thread exit
udpClientT.start()
i=0
key=0
while True:
    i=i+0
    key=kbfunc()
    if key==ord("d"):
        foundsign=True
    if key==ord("s"):
        foundsign=False
    if key==ord("c"):
        udpclient("close")
    if key==ord("u"):
        udpclient("unclose")

print "Exiting Main Thread"
