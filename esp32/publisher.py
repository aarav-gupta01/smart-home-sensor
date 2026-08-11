import umqtt.simple as mqtt # type: ignore[reportMissingImports]
import network # type: ignore[reportMissingImports]
import hidden
import json
import config_esp32



def connect_network():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(hidden.SSID,hidden.PASSWORD)

    print("Connecting...")

    while not wlan.isconnected():
        pass

    print(wlan.ifconfig())

    return wlan


def connect_client():
    client = mqtt.MQTTClient(config_esp32.client_ID, config_esp32.broker_IP, port=config_esp32.port) 
    client.connect()

    return client

def publish_data(client, topic, data):
    payload = json.dumps(data)
    client.publish(topic, payload)