import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
OUT_PIN = 20
EN_PIN = 21
GPIO.setup(EN_PIN, GPIO.OUT)
GPIO.setup(OUT_PIN, GPIO.IN)
GPIO.output(EN_PIN, GPIO.HIGH)

count = 0
is_blocked = False

try:
	while True:
		sensor_value = GPIO.input(OUT_PIN)
		if sensor_value == 0 and not is_blocked:
			count += 1
			print(f"Hand Count: {count}")
			is_blocked = True
		elif sensor_value == 1 and is_blocked:
			is_blocked = False
		time.sleep(0.1)
except KeyboardInterrupt:
	GPIO.cleanup()
	
