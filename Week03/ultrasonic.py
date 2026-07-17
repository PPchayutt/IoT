import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
TRIG = 20
ECHO = 21
GPIO.setup(TRIG,GPIO.OUT)
GPIO.setup(ECHO,GPIO.IN)

#ensure that the Trigger pin is set low, and give the sensor a second to settle.
GPIO.output(TRIG, False)
print ("Waiting For Sensor To Settle")
time.sleep(2)

#trigger pin high for 10uS then set it low again.
GPIO.output(TRIG, True)
time.sleep(0.00001)
GPIO.output(TRIG, False)

#timestamp for ECHO
while GPIO.input(ECHO)==0:
	pulse_start = time.time()
while GPIO.input(ECHO)==1:
	pulse_end = time.time()
pulse_duration = pulse_end - pulse_start
distance = pulse_duration * 17150
distance = round(distance, 2)
print(f"Distance: {distance} cm")

GPIO.cleanup()
