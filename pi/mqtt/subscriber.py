import paho.mqtt.client as mqtt
import json
import config_mqtt

def on_connect(client, userdata, flags, rc):
    print("Connected")
    client.subscribe(config_mqtt.topic_sths34pf80)

def on_message(client, userdata, msg):
    value = json.loads(msg.payload)
    print(msg.topic, value['distance'])

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(config_mqtt.broker_IP, config_mqtt.port, 60)
client.loop_forever()
