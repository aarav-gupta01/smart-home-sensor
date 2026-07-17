from sensors.sths34pf80 import STHS34PF80, make_i2c
from sensors.bme680 import BME680_I2C

from machine import Pin
i2c = make_i2c(scl=33, sda=32)
print(i2c.scan())

bme680 = BME680_I2C(i2c, address=0x76)
sths34pf80 = STHS34PF80(i2c)