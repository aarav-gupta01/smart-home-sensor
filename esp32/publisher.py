import umqtt.simple as mqtt # type: ignore[reportMissingImports]
import network # type: ignore[reportMissingImports]
import hidden
import json
import config_esp32


wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(hidden.SSID,hidden.PASSWORD)

print("Connecting...")
while not wlan.isconnected():
    pass

print(wlan.ifconfig())

data = {'distance': 42}

payload = json.dumps(data)
client = mqtt.MQTTClient(config_esp32.client_ID, config_esp32.broker_IP, port=config_esp32.port)

client.connect()

client.publish(config_esp32.topic_sths34pf80, payload)

client.disconnect()
