import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO

# กำหนดขา GPIO ตามโหมด BCM
PIN_RED = 17
PIN_GREEN = 27
PIN_BLUE = 22

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_RED, GPIO. OUT)
GPIO.setup(PIN_GREEN, GPIO.OUT)
GPIO.setup(PIN_BLUE, GPIO.OUT)

# ตั้งค่าระบบ PWM บนทั้ง 3 ขา (ความถี่ 1000 Hz)
pwm_red = GPIO.PWM(PIN_RED, 1000)
pwm_green = GPIO.PWM(PIN_GREEN, 1000)
pwm_blue = GPIO.PWM(PIN_BLUE, 1000)

pwm_red.start(0)
pwm_green.start(0)
pwm_blue.start(0)

# ตัวแปรจำสถานะแม่สี (0 หรือ 1) และค่าความสว่าง (0 - 100%)
r_state = 0
g_state = 0
b_state = 0
brightness = 100
is_master_on = True

# ฟังก์ชันคำนวณและสั่งระดับความสว่าง PWM ให้แต่ละแม่สี
def update_leds():
    if not is_master_on:
        pwm_red.ChangeDutyCycle(0)
        pwm_green.ChangeDutyCycle(0)
        pwm_blue.ChangeDutyCycle(0)
        return

    # คำนวณ DutyCycle ตามสถานะสีและระดับความสว่าง
    duty_r = brightness if r_state else 100
    duty_g = brightness if g_state else 100
    duty_b = brightness if b_state else 100

    pwm_red.ChangeDutyCycle(duty_r)
    pwm_green.ChangeDutyCycle(duty_g)
    pwm_blue.ChangeDutyCycle(duty_b)
    print(f"-> สถานะไฟ: R={duty_r}%, G={duty_g}%, B={duty_b}% (ความสว่างรวม: {brightness}%)")

# ฟังก์ชันทำงานเมื่อได้รับข้อความผ่าน MQTT
def on_message(client, userdata, msg):
    global r_state, g_state, b_state, brightness, is_master_on
    payload = msg.payload.decode().strip()
    print(f"ได้รับคำสั่ง: {payload}")

    # คำสั่ง Master ON / OFF
    if payload.upper() == "ON":
        is_master_on = True
        update_leds()
    elif payload.upper() == "OFF":
        is_master_on = False
        update_leds()

    # คำสั่งปรับสีแบบผสมแม่สี (Format: COLOR:r,g,b)
    elif payload.startswith("COLOR:"):
        is_master_on = True
        try:
            _, values = payload.split(":")
            r, g, b = map(int, values.split(","))
            r_state, g_state, b_state = r, g, b
            update_leds()
        except Exception as e:
            print("รูปแบบ COLOR ไม่ถูกต้อง:", e)

    # คำสั่งตัวเลขจาก Slider (0 - 100) เพื่อปรับ PWM หรี่/สว่าง
    elif payload.isdigit():
        is_master_on = True
        val = int(payload)
        brightness = max(0, min(100, val)) # ควบคุมค่าให้อยู่ช่วง 0-100
        update_leds()

# เชื่อมต่อ MQTT Broker
mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_message = on_message
mqttc.connect("mqtt-dashboard.com", 1883)

mqttc.subscribe("115/color", qos=1) # Topic เดียวกันกับใน HTML

print("Raspberry Pi พร้อมรับคำสั่งผสมสีและหรี่ไฟ LED แล้ว...")
try:
    mqttc.loop_forever()
except KeyboardInterrupt:
    pwm_red.stop()
    pwm_green.stop()
    pwm_blue.stop()
    GPIO.cleanup()
    print("\nปิดโปรแกรมเรียบร้อย")
