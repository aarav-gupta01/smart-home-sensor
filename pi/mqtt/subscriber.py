import paho.mqtt.client as mqtt
import json
import config_mqtt

def on_connect(client, userdata, flags, rc):
    print("Connected")
    client.subscribe('roomsensor/#')

def on_message(client, userdata, msg):
    payload = json.loads(msg.payload)
    print(msg.topic)
    for key, val in payload.items():
        print(f"{key}: {val}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(config_mqtt.broker_IP, config_mqtt.port, 60)
client.loop_forever()
