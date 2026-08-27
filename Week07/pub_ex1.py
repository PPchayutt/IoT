import paho.mqtt.client as mqtt
import time

# สร้าง MQTT Client เวอร์ชัน 5 พร้อมตั้ง Client ID
mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="raspi-pub-device-01", protocol=mqtt.MQTTv5)

# ตั้งค่า LWT ถ้าหลุดการเชื่อมต่อ ให้ส่งข้อความแจ้งเตือนอัตโนมัติ
mqttc.will_set(
    topic="115/status/pub",
    payload="Publisher OFFLINE",
    qos=1,
    retain=True
)

# เชื่อมต่อไปยัง Broker พอร์ต 1883
mqttc.connect("mqtt-dashboard.com", 1883)

index = 1
print("Publisher เริ่มส่งข้อความ...")
while True:
    message = f"Hello Message #{index}"
    # ส่งข้อความไปยัง topic 115/data ทุก 2 วินาที
    mqttc.publish("115/data", message, qos=1)
    print(f"กำลังส่ง: {message}")
    index += 1
    time.sleep(2)
