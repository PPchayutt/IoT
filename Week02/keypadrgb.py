import RPi.GPIO as GPIO
import time

ROWS = [19, 13, 6, 5]
COLS = [22, 27, 17, 4]

PIN_R = 16
PIN_G = 20
PIN_B = 21

KEYPAD = [
    ['1', '2', '3', 'A'],
    ['4', '5', '6', 'B'],
    ['7', '8', '9', 'C'],
    ['*', '0', '#', 'D']
]

COLORS = {
    '1': (0, 1, 1),
    '2': (1, 0, 1),
    '3': (1, 1, 0),
    '4': (0, 0, 1),
    '5': (1, 0, 0),
    '6': (0, 1, 0),
    '7': (0, 0, 0)
}

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    for row_pin in ROWS:
        GPIO.setup(row_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    for col_pin in COLS:
        GPIO.setup(col_pin, GPIO.OUT)
        GPIO.output(col_pin, GPIO.HIGH)
    for pin in [PIN_R, PIN_G, PIN_B]:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.HIGH)

def set_color(r, g, b):
    GPIO.output(PIN_R, r)
    GPIO.output(PIN_G, g)
    GPIO.output(PIN_B, b)

def turn_off():
    set_color(1, 1, 1)

def loop():
    try:
        while True:
            key_pressed = False
            for col_num, col_pin in enumerate(COLS):
                GPIO.output(col_pin, GPIO.LOW)
                for row_num, row_pin in enumerate(ROWS):
                    if GPIO.input(row_pin) == GPIO.LOW:
                        key = KEYPAD[row_num][col_num]
                        if key in COLORS:
                            r, g, b = COLORS[key]
                            set_color(r, g, b)
                        key_pressed = True
                GPIO.output(col_pin, GPIO.HIGH)
            if not key_pressed:
                turn_off()
            time.sleep(0.05)

    except KeyboardInterrupt:
        turn_off()
        GPIO.cleanup()

if __name__ == '__main__':
    setup()
    loop()
