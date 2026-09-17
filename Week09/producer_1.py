import pika
import json
import time
import random
import ssl
from datetime import datetime

RABBITMQ_HOST = "amqp.iot.kmitl.co"
RABBITMQ_USER = "67070115"
RABBITMQ_PASS = "DnpEbOotak0aJ-BDMgYwEdutpmjwDVIx"

EXCHANGE_NAME = "amq.direct"
ROUTING_KEY = "exercise" # ใช้ Routing Key ใหม่เพื่อไม่ให้ปนกับของเดิม

credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
parameters = pika.ConnectionParameters(
    host=RABBITMQ_HOST, credentials=credentials, port=5671, virtual_host="67070115",
    ssl_options=pika.SSLOptions(ssl.create_default_context())
)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

print("Producer 1 started (Sends every 2s)...")
try:
    while True:
        temp = round(random.uniform(20, 100), 1)
        data = {
            "producer": "P1",
            "timestamp": datetime.now().isoformat(),
            "temperature": temp
        }
        channel.basic_publish(
            exchange=EXCHANGE_NAME,
            routing_key=ROUTING_KEY,
            body=json.dumps(data)
        )
        print(f"[SEND P1] Temp: {temp} °C")
        time.sleep(2) # ส่งทุก 2 วินาที
except KeyboardInterrupt:
    pass
finally:
    connection.close()