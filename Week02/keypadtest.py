import RPi.GPIO as GPIO
import time

# พี่สลับและกลับด้านขา GPIO ให้ตรงกับที่หนูเสียบสายไว้แล้วนะคะ
ROWS = [19, 13, 6, 5]   # เอา COLS เดิมมาเรียงกลับหลัง
COLS = [22, 27, 17, 4]  # เอา ROWS เดิมมาเรียงกลับหลัง

# หน้าตาของปุ่มบน Keypad เหมือนเดิมเลย
KEYPAD = [
    ['1', '2', '3', 'A'],
    ['4', '5', '6', 'B'],
    ['7', '8', '9', 'C'],
    ['*', '0', '#', 'D']
]

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    for row_pin in ROWS:
        GPIO.setup(row_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
    for col_pin in COLS:
        GPIO.setup(col_pin, GPIO.OUT)
        GPIO.output(col_pin, GPIO.HIGH)

def test_keypad():
    print("เริ่มทดสอบ Keypad! กดปุ่มได้เลยค่ะ (กด Ctrl+C เพื่อหยุดโปรแกรม)")
    try:
        while True:
            for col_num, col_pin in enumerate(COLS):
                GPIO.output(col_pin, GPIO.LOW)
                
                for row_num, row_pin in enumerate(ROWS):
                    if GPIO.input(row_pin) == GPIO.LOW:
                        key = KEYPAD[row_num][col_num]
                        print(f"ปุ่มที่กดคือ: {key}")
                        time.sleep(0.3)
                
                GPIO.output(col_pin, GPIO.HIGH)
            time.sleep(0.01)
            
    except KeyboardInterrupt:
        print("\nจบการทดสอบจ้า เก่งมากเลย!")
        GPIO.cleanup()

if __name__ == '__main__':
    setup()
    test_keypad()
