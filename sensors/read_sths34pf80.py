import time
import adafruit_sths34pf80  # type: ignore[reportMissingImports]
import board  # type: ignore[reportMissingImports]

i2c = board.I2C()
sensor = adafruit_sths34pf80.STHS34PF80(i2c)

while True:
    if sensor.data_ready:
        ambient_temp = sensor.ambient_temperature
        object_temp = sensor.object_temperature
        comp_object_temp = sensor.compensated_object_temperature

        presence_value = sensor.presence_value
        motion_value = sensor.motion_value
        temp_shock_value = sensor.temperature_shock_value

        presence = sensor.presence
        motion = sensor.motion
        temp_shock = sensor.temperature_shock

        print(f"Ambient Temperature: {ambient_temp:.2f} °C")
        print(f"Object Temperature: {object_temp}")
        print(f"Compensated Object Temperature: {comp_object_temp}")
        print(f"Presence Value: {presence_value} {'[DETECTED]' if presence else '[NOT DETECTED]'}")
        print(f"Motion Value: {motion_value} {'[DETECTED]' if motion else '[NOT DETECTED]'}")
        print(f"Temperature Shock Value: {temp_shock_value} {'[DETECTED]' if temp_shock else '[NOT DETECTED]'}")
    time.sleep(1)
