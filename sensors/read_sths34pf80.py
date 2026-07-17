import time
import adafruit_sths34pf80  # type: ignore[reportMissingImports]
import board # type: ignore[reportMissingImports]

i2c = board.I2C()
sths34pf80 = adafruit_sths34pf80.STHS34PF80(i2c)

while True:
    if sths34pf80.data_ready:
        ambient_temp = sths34pf80.ambient_temperature
        object_temp = sths34pf80.object_temperature
        comp_object_temp = sths34pf80.compensated_object_temperature

        presence_value = sths34pf80.presence_value
        motion_value = sths34pf80.motion_value
        temp_shock_value = sths34pf80.temperature_shock_value

        presence = sths34pf80.presence
        motion = sths34pf80.motion
        temp_shock = sths34pf80.temperature_shock

        print(f"Ambient Temperature: {ambient_temp:.2f} °C")
        print(f"Object Temperature: {object_temp}")
        print(f"Compensated Object Temperature: {comp_object_temp}")
        print(f"Presence Value: {presence_value} {'[DETECTED]' if presence else '[NOT DETECTED]'}")
        print(f"Motion Value: {motion_value} {'[DETECTED]' if motion else '[NOT DETECTED]'}")
        print(f"Temperature Shock Value: {temp_shock_value} {'[DETECTED]' if temp_shock else '[NOT DETECTED]'}")
    time.sleep(1)
