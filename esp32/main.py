import time
from sensors.sths34pf80 import STHS34PF80, make_i2c
from sensors.bme680 import BME680_I2C

from machine import Pin

#Initialize I2C Bus
i2c = make_i2c(scl=33, sda=32)
print(i2c.scan())

#Initialize Sensors
bme680 = BME680_I2C(i2c, address=0x76)
sths34pf80 = STHS34PF80(i2c)

#Loop to read STHS34PF80 and BME680
while True:
    if sths34pf80.data_ready:
        
        ambient_temp = sths34pf80.ambient_temperature
        #object_temp = sths34pf80.object_temperature                    Unnecessary Values
        #comp_object_temp = sths34pf80.compensated_object_temperature                    Unnecessary Values

        presence_value = sths34pf80.presence_value
        motion_value = sths34pf80.motion_value
        temp_shock_value = sths34pf80.temperature_shock_value

        presence = sths34pf80.presence
        motion = sths34pf80.motion
        temp_shock = sths34pf80.temperature_shock

        print("Ambient Temperature: %.2f C" % ambient_temp)
        #print("Object Temperature: %s" % object_temp)                    Unnecessary Values
        #print("Compensated Object Temperature: %s" % comp_object_temp)                    Unnecessary Values
        print(
                "Presence Value: %s %s"
                % (presence_value, "[DETECTED]" if presence else "[NOT DETECTED]"))
        print(
                "Motion Value: %s %s"
                % (motion_value, "[DETECTED]" if motion else "[NOT DETECTED]")
            )
        print(
                "Temperature Shock Value: %s %s"
                % (temp_shock_value, "[DETECTED]" if temp_shock else "[NOT DETECTED]")
            )
        
    if bme680:
    
        bme680.sea_level_pressure = 1013.25

        temperature_offset = -5

        temperature = bme680.temperature + temperature_offset
        gas = bme680.gas
        humidity = bme680.humidity
        pressure = bme680.pressure
        altitude = bme680.altitude

        print(f"\nTemperature: {temperature:0.1f} C")
        print(f"Gas: {gas:d} ohm")
        print(f"Humidity: {humidity:.1f} %")
        print(f"Pressure: {pressure:.3f} hPa")
        print(f"Altitude = {altitude:.2f} meters")

    time.sleep(1)