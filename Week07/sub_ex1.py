import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO

# ตั้งค่าขาควบคุมไฟ LED (GPIO 18)
LED_PIN = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.output(LED_PIN, GPIO.LOW)

# ฟังก์ชันทำงานเมื่อมีข้อความส่งเข้ามา
def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode().strip()
    print(f"ได้รับข้อความ -> Topic: {topic} | Data: {payload}")

    # ตรวจสอบคำสั่งควบคุมไฟ LED จาก Web Browser
    if topic == "115/led":
        if payload.upper() == "ON":
            GPIO.output(LED_PIN, GPIO.HIGH)
            print(">>> [LED ติด] <<<")
        elif payload.upper() == "OFF":
            GPIO.output(LED_PIN, GPIO.LOW)
            print(">>> [LED ดับ] <<<")

# กำหนด Client ID คงที่เพื่อใช้งาน Session Management
mqttc = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id="raspi-sub-session-01",
    protocol=mqtt.MQTTv5
)
mqttc.on_message = on_message

# ตั้งค่า LWT เมื่อ Subscriber หลุดการเชื่อมต่อ
mqttc.will_set(
    topic="115/status/sub",
    payload="Subscriber OFFLINE",
    qos=1,
    retain=True
)

# กำหนดให้ Broker จำ Session ไว้ 3600 วินาที
properties = mqtt.Properties(mqtt.PacketTypes.CONNECT)
properties.SessionExpiryInterval = 3600

# เชื่อมต่อโดยตั้ง clean_start=False เพื่อดึงข้อความย้อนหลังได้
mqttc.connect(
    "mqtt-dashboard.com",
    1883,
    clean_start=False,
    properties=properties
)

# Subscribe Topic รับข้อมูล และ Topic ควบคุม LED (ใช้ QoS 1)
mqttc.subscribe("115/data", qos=1)
mqttc.subscribe("115/led", qos=1)

print("Subscriber พร้อมรับข้อความและคำสั่งควบคุมไฟ...")
try:
    mqttc.loop_forever()
except KeyboardInterrupt:
    GPIO.cleanup()
    print("\nปิดโปรแกรมเรียบร้อย")
