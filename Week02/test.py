import time
import spidev
spi = spidev.SpiDev() # Open SPI bus
spi.open(0, 0)
spi.max_speed_hz = 500000
def ReadChannel(channel): # read channel (0-7) from MCP3208
	adc = spi.xfer2([6 | (channel & 4) >> 2, (channel & 3) << 6, 0])
	#ส่งข้อมูล3 byte ตามที่ Datasheet กาหนด แล้วรอรับค่าที่แปลงได้
	data = ((adc[1] & 15) << 8) + adc[2]
	return data
while True:
	reading = ReadChannel(0)
	voltage = reading * 3.3 / 4096
	print("Reading=%d\t Voltage=%f" % (reading, voltage))
	time.sleep(1)
