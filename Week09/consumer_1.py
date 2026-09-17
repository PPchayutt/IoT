import pika
import json
import ssl

RABBITMQ_HOST = "amqp.iot.kmitl.co"
RABBITMQ_USER = "67070115"
RABBITMQ_PASS = "DnpEbOotak0aJ-BDMgYwEdutpmjwDVIx"

EXCHANGE_NAME = "amq.direct"
ROUTING_KEY = "exercise"
QUEUE_NAME = "queue_all" # คิวสำหรับรับทุกค่า

credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
parameters = pika.ConnectionParameters(
    host=RABBITMQ_HOST, credentials=credentials, port=5671, virtual_host="67070115",
    ssl_options=pika.SSLOptions(ssl.create_default_context())
)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

# ประกาศสร้างคิวและ Bind เข้ากับ Routing Key
channel.queue_declare(queue=QUEUE_NAME, durable=True)
channel.queue_bind(exchange=EXCHANGE_NAME, queue=QUEUE_NAME, routing_key=ROUTING_KEY)

def callback(ch, method, properties, body):
    data = json.loads(body)
    print(f"[ALL DATA] From: {data['producer']} | Temp: {data['temperature']} °C")
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=False)
print("Consumer 1 (Show ALL) started...")
channel.start_consuming()