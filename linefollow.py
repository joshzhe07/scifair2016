import RPi.GPIO as GPIO
import time


GPIO.setwarnings(False)

left_motor_1 = 6
left_motor_2 = 5
right_motor_1 = 12
right_motor_2 = 13
speed = 40
READR = 27
READL = 17

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




while (True):

    if GPIO.input(READR) == 0 and GPIO.input(READL) == 0:
        left_1.start(speed)
        left_2.start(speed*0)
        right_1.start(speed)
        right_2.start(speed*0)

    if GPIO.input(READR) == 0 and GPIO.input(READL) == 1:
        left_1.start(speed)
        left_2.start(speed*0)
        right_1.start(speed*0)
        right_2.start(speed*0)

    if GPIO.input(READR) == 1 and GPIO.input(READL) == 0:
        left_1.start(speed*0)
        left_2.start(speed*0)
        right_1.start(speed)
        right_2.start(speed*0)
