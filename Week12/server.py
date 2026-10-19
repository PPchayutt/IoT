import os
import time
import json
import logging
import threading
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
from mcp.server import MCPServer
from mcp.server.transport_security import TransportSecuritySettings

# กำหนดขา GPIO (โหมด BCM) สำหรับไฟ LED และ Ultrasonic
LIGHT = 4   # ขาไฟ LED ที่ GPIO 4 (เข็ม Pin 7)
TRIG = 23   # ขา TRIG ของ Ultrasonic ที่ GPIO 23 (เข็ม Pin 16)
ECHO = 24   # ขา ECHO ของ Ultrasonic ที่ GPIO 24 (เข็ม Pin 18)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(LIGHT, GPIO.OUT)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.output(TRIG, GPIO.LOW)

logging.basicConfig(level=logging.INFO)

# ตั้งค่า MQTT Broker และ Topics
BROKER = os.getenv("MQTT_BROKER", "mqtt-dashboard.com")
PORT = 1883

DEVICE_ID = "mcp-115"
COMMAND_TOPIC = f"{DEVICE_ID}/command"
STATUS_TOPIC = f"{DEVICE_ID}/person"
TEMP_TOPIC = f"{DEVICE_ID}/temperature"  # เพิ่ม Topic รับค่าอุณหภูมิจาก Arduino

person_status = None
latest_temperature = None
status_lock = threading.Lock()

# ตั้งค่า MQTT Client
mqtt_client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id="raspi-iot-mcp-pitchayut"
)

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        # Subscribe Topic
        client.subscribe(STATUS_TOPIC)
        client.subscribe(TEMP_TOPIC)
        logging.info(f"MQTT connected! Subscribed to {STATUS_TOPIC} and {TEMP_TOPIC}")

def on_message(client, userdata, msg):
    global person_status, latest_temperature
    payload_str = msg.payload.decode("utf-8").strip()

    with status_lock:
        if msg.topic == STATUS_TOPIC:
            person_status = payload_str
        elif msg.topic == TEMP_TOPIC:
            # รองรับทั้งข้อความ JSON เช่น {"temperature": 31.2} และตัวเลขธรรมดา เช่น 31.2
            try:
                data = json.loads(payload_str)
                if isinstance(data, dict) and "temperature" in data:
                    latest_temperature = str(data["temperature"])
                else:
                    latest_temperature = payload_str
            except json.JSONDecodeError:
                latest_temperature = payload_str
            logging.info(f"Received temperature: {latest_temperature} °C")

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.connect(BROKER, PORT, 60)
mqtt_client.loop_start()

# สร้าง MCP Server
mcp = MCPServer("RaspberryPi-IoT")

# รายการ MCP Tools ทั้งหมด 5 ตัว
# Tool ตัวที่ 1: สั่งเปิด/ปิดไฟผ่านการส่งข้อความไปที่ MQTT Broker และคุม GPIO
@mcp.tool()
def set_led(action: str) -> str:
    """Turn the IoT LED on or off.
    action must be exactly 'on' or 'off'.
    """
    action = action.strip().lower()

    if action not in ("on", "off"):
        return "Error: action must be on or off"

    # สั่งเปิด/ปิดไฟที่ขา GPIO 4 ไปพร้อมกับการส่ง MQTT
    if action == "on":
        GPIO.output(LIGHT, GPIO.HIGH)
    else:
        GPIO.output(LIGHT, GPIO.LOW)

    # Publish เฉพาะคำสั่งที่อนุญาต (แปลงเป็นตัวพิมพ์ใหญ่ ON / OFF)
    info = mqtt_client.publish(
        COMMAND_TOPIC,
        action.upper(),
        qos=1
    )
    info.wait_for_publish(timeout=5)

    if info.rc != mqtt.MQTT_ERR_SUCCESS:
        return "MQTT publish failed"

    return f"Sent LED command: {action.upper()}"

# Tool ตัวที่ 2: สั่งเปิด/ปิดไฟ LED ที่ต่ออยู่กับขา GPIO 4 บน Raspberry Pi โดยตรง
@mcp.tool()
def set_led_raspi(action: str) -> str:
    """Turn Raspberry Pi LED on or off."""
    action = action.strip().lower()

    if action == "on":
        GPIO.output(LIGHT, GPIO.HIGH)
        return "LED is ON"

    if action == "off":
        GPIO.output(LIGHT, GPIO.LOW)
        return "LED is OFF"

    return "Error: action must be on or off"

# Tool ตัวที่ 3: อ่านสถานะการตรวจจับบุคคลล่าสุดจาก MQTT Topic
@mcp.tool()
def get_person_status() -> str:
    """Get the latest person detection status from the camera."""
    with status_lock:
        status = person_status

    if status is None:
        return (
            "No camera status received yet. "
            "Check that the AI camera publishes to "
            + STATUS_TOPIC
        )

    return f"Latest camera status: {status}"

# Tool ตัวที่ 4: วัดค่าระยะทางจาก Ultrasonic Sensor (HC-SR04)
@mcp.tool()
def get_distance() -> str:
    """Get the distance measured by the Ultrasonic sensor (HC-SR04) on Raspberry Pi in centimeters (cm)."""
    
    # วัดระยะทางซ้ำสูงสุด 3 รอบ เพื่อป้องกันค่า Error จาก Linux OS lag
    for _ in range(3):
        GPIO.output(TRIG, GPIO.LOW)
        time.sleep(0.05)

        GPIO.output(TRIG, GPIO.HIGH)
        time.sleep(0.00001)
        GPIO.output(TRIG, GPIO.LOW)

        timeout = time.time() + 0.1
        pulse_start = time.time()
        while GPIO.input(ECHO) == 0:
            pulse_start = time.time()
            if pulse_start > timeout:
                break # หมดเวลาข้ามไปวัดใหม่

        pulse_end = time.time()
        while GPIO.input(ECHO) == 1:
            pulse_end = time.time()
            if pulse_end > timeout:
                break # หมดเวลาข้ามไปวัดใหม่

        pulse_duration = pulse_end - pulse_start
        distance = round((pulse_duration * 34300) / 2, 2)

        # ถ้าระยะทางอยู่ในช่วงที่สมเหตุสมผล (2 cm - 400 cm) ให้ส่งค่ากลับทันที
        if 2 <= distance <= 400:
            return f"Distance: {distance} cm"
            
        time.sleep(0.1) # พักแป๊บนึงก่อนลองวัดใหม่

    return "Error: Could not get a stable reading. Make sure there is an obstacle within 4 meters."

# Tool ตัวที่ 5: อ่านค่าอุณหภูมิล่าสุดที่รับมาจาก Arduino ผ่าน MQTT
@mcp.tool()
def get_temperature() -> str:
    """Get the latest temperature value in Celsius received from the Arduino sensor via MQTT."""
    with status_lock:
        temp = latest_temperature

    if temp is None:
        return (
            "No temperature data received yet. "
            "Check that the Arduino publishes to "
            + TEMP_TOPIC
        )

    return f"Current temperature: {temp} °C"

if __name__ == "__main__":
    security = TransportSecuritySettings(
        allowed_hosts=[
            "pure-canyon-ccffaed0.tunnl.gg",
            "pure-canyon-ccffaed0.tunnl.gg:*",
            "localhost:8000",
            "127.0.0.1:8000",
            "0.0.0.0:8000",
        ],
        allowed_origins=[
            "https://pure-canyon-ccffaed0.tunnl.gg/",
        ],
    )

    mcp.run(
        transport="streamable-http",
        transport_security=security,
        host="0.0.0.0"
    )
