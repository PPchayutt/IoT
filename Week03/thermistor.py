import spidev
import time
import math

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000

def ReadChannel(channel):
    adc = spi.xfer2([6 | (channel & 4) >> 2, (channel & 3) << 6, 0])
    data = ((adc[1] & 15) << 8) + adc[2]
    return data

B = 4050.0
T0 = 298.15
R0 = 10000.0

print("Start")

try:
    while True:
        adc_value = ReadChannel(0)
        voltage = (adc_value * 3.3) / 4096.0
        if voltage > 0 and voltage < 3.3:
            R_thermistor = (voltage * 10000.0) / (3.3 - voltage)
            temp_K = (T0 * B) / (T0 * math.log(R_thermistor / R0) + B)
            temp_C = temp_K - 273.15
            print(f"Voltage: {voltage:.2f}V | Resistor: {R_thermistor:.0f} Ohm | Temp: {temp_C:.2f} °C")
        else:
            print("Error")
        time.sleep(1)

except KeyboardInterrupt:
    print("Stop️")
    spi.close()
