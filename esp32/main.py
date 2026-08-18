import time
import publisher
import config_esp32
from sensors.sths34pf80 import STHS34PF80, make_i2c
from sensors.bme680 import BME680_I2C


#Initialize I2C Bus
i2c = make_i2c(scl=33, sda=32)
print(i2c.scan())

#Initialize Sensors
bme680 = BME680_I2C(i2c, address=0x76)
sths34pf80 = STHS34PF80(i2c)

#Initialize network/MQTT
client = None
while client is None:
    network_object = publisher.connect_network()
    if network_object != None:
        try:
            wlan = network_object
            client = publisher.connect_client()
        except OSError:
            print("Broker Unreachable, retrying...")

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

        #STHS34PF80 print statements from testing phase

        # print("Ambient Temperature: %.2f C" % ambient_temp)
        # #print("Object Temperature: %s" % object_temp)                    Unnecessary Values
        # #print("Compensated Object Temperature: %s" % comp_object_temp)                    Unnecessary Values
        # print(
        #         "Presence Value: %s %s"
        #         % (presence_value, "[DETECTED]" if presence else "[NOT DETECTED]"))
        # print(
        #         "Motion Value: %s %s"
        #         % (motion_value, "[DETECTED]" if motion else "[NOT DETECTED]")
        #     )
        # print(
        #         "Temperature Shock Value: %s %s"
        #         % (temp_shock_value, "[DETECTED]" if temp_shock else "[NOT DETECTED]")
        #     )

        sths_data = {
            "ambient_temp": ambient_temp,
            "presence": presence,
            "presence_value": presence_value,
            "motion": motion,
            "motion_value": motion_value,
            "temp_shock": temp_shock,
            "temp_shock_value": temp_shock_value
        }

        try:
            publisher.publish_data(client, config_esp32.topic_sths34pf80, sths_data)
        except OSError:
             network_object = publisher.connect_network()
             if network_object != None:
                wlan = network_object
                try:
                    client = publisher.connect_client()
                except OSError:
                    print("Broker Unreachable, retrying...")

    # BME680 values
    bme680.sea_level_pressure = 1013.25

    temperature_offset = -5

    temperature = bme680.temperature + temperature_offset
    gas = bme680.gas
    humidity = bme680.humidity
    pressure = bme680.pressure
    altitude = bme680.altitude


    #BME680 print statements from testing phase

    # print(f"\nTemperature: {temperature:0.1f} C")
    # print(f"Gas: {gas:d} ohm")
    # print(f"Humidity: {humidity:.1f} %")
    # print(f"Pressure: {pressure:.3f} hPa")
    # print(f"Altitude = {altitude:.2f} meters")

    bme680_data = {
        "temperature": temperature,
        "gas": gas,
        "humidity": humidity,
        "pressure": pressure,
        "altitude": altitude
    }

    try:
        publisher.publish_data(client, config_esp32.topic_bme680, bme680_data)
    except OSError:
        network_object = publisher.connect_network()
        if network_object != None:
            wlan = network_object
            try:
                client = publisher.connect_client()
            except OSError:
                print("Broker Unreachable, retrying...")

    time.sleep(1)
