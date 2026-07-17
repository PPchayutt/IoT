import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
LDR_PIN = 20
LED_PIN = 21
GPIO.setup(LDR_PIN, GPIO.IN)
GPIO.setup(LED_PIN, GPIO.OUT)

print("Start")

while True:
    is_dark = GPIO.input(LDR_PIN)
    
    if is_dark == 1:
        GPIO.output(LED_PIN, GPIO.HIGH)
    else:
        GPIO.output(LED_PIN, GPIO.LOW)
        
    time.sleep(0.1)
