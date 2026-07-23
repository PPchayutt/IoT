import smbus3
import time
from RPLCD.i2c import CharLCD

lcd = CharLCD('PCF8574', 0x27)
bus = smbus3.SMBus(1)

try:
    while True:
        bus.i2c_wr(0x44, [0x2C, 0x06])
        time.sleep(0.5)
        msg = bus.i2c_rd(0x44, 6)
        data = bytes(msg)
        temp = data[0] * 256 + data[1]
        cTemp = -45 + (175 * temp / 65535.0)
        humidity = 100 * (data[3] * 256 + data[4]) / 65535.0
        lcd.clear()
        lcd.write_string("Temp: %.2f C" % cTemp)
        lcd.crlf() 
        lcd.write_string("Humid: %.2f %%" % humidity)
        time.sleep(2)

except KeyboardInterrupt:
    lcd.clear()
    bus.close()
