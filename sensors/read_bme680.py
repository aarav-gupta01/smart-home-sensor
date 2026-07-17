import time
import board # type: ignore[reportMissingImports]
import adafruit_bme680 # type: ignore[reportMissingImports]

i2c = board.I2C()
bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c, debug=False)