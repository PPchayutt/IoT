import RPi.GPIO as GPIO
import spidev
import time

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 500000

def ReadChannel(channel):
    adc = spi.xfer2([6 | (channel & 4) >> 2, (channel & 3) << 6, 0])
    data = ((adc[1] & 15) << 8) + adc[2]
    return data

LED_PIN = 12
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(LED_PIN, GPIO.OUT)
led_pwm = GPIO.PWM(LED_PIN, 1000)
led_pwm.start(0)

try:
     while True:
        adc_value = ReadChannel(0)
        duty_cycle = (adc_value / 4095.0) * 100.0
        led_pwm.ChangeDutyCycle(duty_cycle)
        print(f"ADC: {adc_value} -> Brightness: {duty_cycle:.1f}%")
        time.sleep(0.1)

except KeyboardInterrupt:
    led_pwm.stop()
    GPIO.cleanup()
