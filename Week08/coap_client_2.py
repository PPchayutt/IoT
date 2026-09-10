import asyncio
from aiocoap import Context, Message
import aiocoap

# นำ IP ของ Raspberry Pi มาใส่ให้ถูกต้อง
SERVER_IP = "10.156.11.248" 
SERVER_PORT = 5683

async def led_pwm(value):
    protocol = await Context.create_client_context()
    request = Message(
        code=aiocoap.Code.PUT,
        uri=f"coap://{SERVER_IP}:{SERVER_PORT}/led",
        payload=str(value).encode() # ส่งค่าความสว่างเป็น byte
    )
    response = await protocol.request(request).response
    print(f"Sent: {value}% | Code: {response.code}")

async def main():
    # ทดสอบส่งค่าความสว่างไปที่ Server
    print("ทดสอบหรี่ไฟ LED ที่ 25%")
    await led_pwm(25)
    await asyncio.sleep(2)

    print("ทดสอบเร่งไฟ LED ที่ 80%")
    await led_pwm(80)
    await asyncio.sleep(2)

    print("ทดสอบปิดไฟ LED (0%)")
    await led_pwm(0)

asyncio.run(main())
