
from RPLCD.i2c import CharLCD
import time

# สร้างออบเจ็กต์ LCD
lcd = CharLCD(
	i2c_expander='PCF8574',
	address=0x27,
	port=1,
	cols=16,
	rows=2,
	charmap='A00',
	auto_linebreaks=True,
	backlight_enabled=True
)
# แสดงข้อความ
lcd.write_string("Hello, Opto")
lcd.crlf() # ขึ้นบรรทัดใหม่
lcd.write_string("67 67!")

