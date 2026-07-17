import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
PIN_R = 14
PIN_G = 15
PIN_B = 18

GPIO.setup(PIN_R, GPIO.OUT)
GPIO.setup(PIN_G, GPIO.OUT)
GPIO.setup(PIN_B, GPIO.OUT)

def set_color(r, g, b):
    GPIO.output(PIN_R, r)
    GPIO.output(PIN_G, g)
    GPIO.output(PIN_B, b)

while True:
    set_color(True, False, False)
    time.sleep(1)

    set_color(False, True, False)
    time.sleep(1)

    set_color(False, False, True)
    time.sleep(1)

    set_color(True, True, False)
    time.sleep(1)

    set_color(False, True, True)
    time.sleep(1)

    set_color(True, False, True)
    time.sleep(1)

    set_color(True, True, True)
    time.sleep(1)