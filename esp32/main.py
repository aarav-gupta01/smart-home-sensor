from sensors.sths34pf80 import STHS34PF80, make_i2c
from sensors.bme680 import BME680

from machine import Pin
i2c = make_i2c(scl=33, sda=32)
print(i2c.scan())

bme680 = BME680(i2c)
sths34pf80 = STHS34PF80(i2c)