import umqtt.simple as mqtt # type: ignore[reportMissingImports]
import network # type: ignore[reportMissingImports]
import hidden
import json
import time
import config_esp32

out_of_time = 10000

def connect_network():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(hidden.SSID,hidden.PASSWORD)

    print("Connecting...")

    start_time = time.ticks_ms()

    while not wlan.isconnected() and time.ticks_diff(time.ticks_ms(), start_time) <= out_of_time:
        pass

    if wlan.isconnected():
        print(wlan.ifconfig())
        return wlan
    else:
        print(wlan.status())
        return None


def connect_client():
    client = mqtt.MQTTClient(config_esp32.client_ID, config_esp32.broker_IP, port=config_esp32.port) 
    client.connect()

    return client

def publish_data(client, topic, data):
    payload = json.dumps(data)
    client.publish(topic, payload)
    