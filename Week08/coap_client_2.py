import asyncio
import aiocoap
from aiocoap import Context, Message, Code

# ===== ตั้งค่า IP และ Port ของ Arduino CoAP Server =====
SERVER_IP = "10.156.11.217"  # เปลี่ยนเป็น IP ของ Arduino UNO R4
SERVER_PORT = 5683

# ===== ตั้งค่าขา GPIO สำหรับ LED บน Raspberry Pi =====
LED_PIN = 17  # ขา BCM GPIO 17 (ขา Pin 11 บนบอร์ด)
PWM_FREQUENCY = 100  # ความถี่ 100 Hz

# ตรวจสอบและเริ่มต้นใช้งาน RPi.GPIO
pwm = None
try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LED_PIN, GPIO.OUT)
    pwm = GPIO.PWM(LED_PIN, PWM_FREQUENCY)
    pwm.start(0)  # เริ่มต้นที่ 0% (ปิดไฟ)
    print(f"[GPIO] Initialized LED on GPIO {LED_PIN} with PWM at {PWM_FREQUENCY}Hz")
except (ImportError, RuntimeError) as e:
    print(f"[GPIO Warning] RPi.GPIO is not available ({e}). Running in simulation mode.")


def set_led_duty_cycle(duty_cycle: float):
    """ปรับความสว่างของ LED ตามค่า Duty Cycle (0 - 100%)"""
    duty = max(0.0, min(100.0, duty_cycle))
    if pwm is not None:
        pwm.ChangeDutyCycle(duty)
    return duty


def voltage_to_duty_cycle(voltage: float) -> float:
    """
    Scale ค่าแรงดัน (0.0 - 5.0 V) ให้อยู่ในช่วง Duty Cycle (0.0 - 100.0 %)
    ตามคำใบ้ Hint: เมื่ออ่านค่าแรงดันแล้ว ให้ Scale ให้อยู่ในช่วง 0-100
    """
    clamped_voltage = max(0.0, min(5.0, voltage))
    duty_cycle = (clamped_voltage / 5.0) * 100.0
    return duty_cycle


async def get_potentiometer_voltage():
    """
    ฟังก์ชันสำหรับทดสอบส่ง GET Request ไปยัง CoAP Server บน Arduino
    เพื่ออ่านค่าแรงดันของตัวต้านทานปรับค่าได้
    """
    print("\n--- [1] Performing CoAP GET Request ---")
    protocol = await Context.create_client_context()
    uri = f"coap://{SERVER_IP}:{SERVER_PORT}/potentiometer"
    request = Message(code=Code.GET, uri=uri)

    try:
        response = await protocol.request(request).response
        payload_str = response.payload.decode("utf-8").strip()
        voltage = float(payload_str.replace("V", "").replace("v", "").strip())
        duty_cycle = voltage_to_duty_cycle(voltage)

        print(f"Request URI      : {uri}")
        print(f"Response Code    : {response.code}")
        print(f"Voltage Read     : {voltage:.2f} V (0 - 5V)")
        print(f"Scaled Duty Cycle: {duty_cycle:.1f} % (0 - 100%)")

        set_led_duty_cycle(duty_cycle)
        print(f"LED Brightness set to: {duty_cycle:.1f}%")
        return voltage
    except Exception as e:
        print(f"[GET Error] Failed: {e}")
        return None


def observation_callback(response):
    """
    Callback function ที่จะทำงานทุกครั้งเมื่อ CoAP Server (Arduino)
    ส่งข้อมูล Notify เมื่อมีการหมุนตัวต้านทานปรับค่าได้ (Observe Feature)
    """
    if response.code.is_successful():
        payload_str = response.payload.decode("utf-8").strip()
        try:
            voltage = float(payload_str.replace("V", "").replace("v", "").strip())
            duty_cycle = voltage_to_duty_cycle(voltage)
            set_led_duty_cycle(duty_cycle)
            print(f"[Observe Notification] Voltage: {voltage:4.2f} V -> LED Duty Cycle: {duty_cycle:5.1f}%")
        except ValueError:
            print(f"[Observe Notification] Received raw payload: {payload_str}")
    else:
        print(f"[Observe Error] Notification code: {response.code}")


async def observe_potentiometer():
    """
    ฟังก์ชันสำหรับลงทะเบียนและรับข้อมูลแบบ Observe (RFC 7641) จาก Arduino
    """
    print("\n--- [2] Starting CoAP Observe Mode ---")
    protocol = await Context.create_client_context()
    uri = f"coap://{SERVER_IP}:{SERVER_PORT}/potentiometer"

    request = Message(code=Code.GET, uri=uri)
    request.opt.observe = 0  # 0 = Register Observe

    protocol_request = protocol.request(request)
    protocol_request.observation.register_callback(observation_callback)

    try:
        initial_response = await protocol_request.response
        print(f"Observe established with {uri} (Response: {initial_response.code})")
        # ประมวลผลค่าเริ่มต้นทันที
        observation_callback(initial_response)

        print("\n>> Ready! หมุนตัวต้านทานปรับค่าได้ที่ Arduino เพื่อปรับความสว่าง LED บน Raspberry Pi")
        print(">> กด Ctrl + C เพื่อออกจากโปรแกรม\n")

        # รอรับการแจ้งเตือนต่อไปอย่างต่อเนื่อง
        await asyncio.get_running_loop().create_future()
    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"[Observe Error] Connection error: {e}")


async def main():
    # 1. ทดสอบ GET Request ค่าจาก Potentiometer 1 ครั้ง
    await get_potentiometer_voltage()
    await asyncio.sleep(2)

    # 2. เริ่มทำงานในโหมด Observe เพื่อรับค่าอย่างต่อเนื่อง
    await observe_potentiometer()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
    finally:
        if pwm is not None:
            pwm.stop()
        try:
            import RPi.GPIO as GPIO
            GPIO.cleanup()
            print("[GPIO] Cleaned up successfully.")
        except Exception:
            pass
