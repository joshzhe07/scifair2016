# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import sys

sys.path.append('/usr/local/lib/python2.7/site-packages')

import cv2
import numpy as np

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 50
camera.vflip = True

rawCapture = PiRGBArray(camera, size=(640, 480))

# allow the camera to warmup
time.sleep(0.1)

# capture frames from the camera
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
        if len(contours) > 0:
	          cnt = sorted(contours, key = cv2.contourArea, reverse = True)[0]
                  rect = np.int32(cv2.boxPoints(cv2.minAreaRect(cnt)))
                  cv2.drawContours(blur, [rect], -1, (0, 255, 0), 2)
                  #print "rect",rect
                  #print "%dpx %.2fft" % (rect[1][0],rect[1][0]/focallen)
                  #print "%dpx %dpx" % (rect[1][0],rect[1][1])
                  width=rect[2][0]-rect[1][0]
                  height=rect[0][1]-rect[1][1]
                #   print "%dpx %dpx" % (width,height)
                  print "%dpx" % (height)
                #   debugfile.write(str(width)+';'+str(height) + "\n")

                  if height>100:
                      print "car1 found the stop sign"

        # cv2.imshow("Frame", blur)
        cv2.imshow('thresh',thresh2)
        key = cv2.waitKey(1) & 0xFF

	# clear the stream in preparation for the next frame
        rawCapture.truncate(0)

	# if the `q` key was pressed, break from the loop
        if key == ord("q"):
        	break
