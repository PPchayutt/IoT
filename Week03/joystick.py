
import RPi.GPIO as GPIO
import spidev
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

SW_PIN = 21
R_PIN = 17
G_PIN = 27
B_PIN = 22

GPIO.setup(R_PIN, GPIO.OUT)
GPIO.setup(G_PIN, GPIO.OUT)
GPIO.setup(B_PIN, GPIO.OUT)
GPIO.setup(SW_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

pwm_r = GPIO.PWM(R_PIN, 100)
pwm_g = GPIO.PWM(G_PIN, 100)
pwm_b = GPIO.PWM(B_PIN, 100)

pwm_r.start(0)
pwm_g.start(0)
pwm_b.start(0)

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000

def ReadChannel(channel):
    adc = spi.xfer2([6 | (channel & 4) >> 2, (channel & 3) << 6, 0])
    data = ((adc[1] & 15) << 8) + adc[2]
    return data

print("Start")
print("Rotate for Red/Blue")
print("Button for Green")

try:
    green_on = False
    last_sw_state = 1
    while True:
        x_val = ReadChannel(0)
        y_val = ReadChannel(1)
        r_brightness = x_val / 40.95
        b_brightness = y_val / 40.95
        pwm_r.ChangeDutyCycle(r_brightness)
        pwm_b.ChangeDutyCycle(b_brightness)
        current_sw_state = GPIO.input(SW_PIN)
        if current_sw_state == 0 and last_sw_state == 1:
            green_on = not green_on
            if green_on:
                pwm_g.ChangeDutyCycle(100)
            else:
                pwm_g.ChangeDutyCycle(0)
        last_sw_state = current_sw_state
        time.sleep(0.05)

except KeyboardInterrupt:
    print("Stop")
    pwm_r.stop()
    pwm_g.stop()
    pwm_b.stop()
    spi.close()
    GPIO.cleanup()
