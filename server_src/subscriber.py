import paho.mqtt.client as paho
from gps import gps_operations
from wifi import wifi_operations


MQTT_BROKER_HOST = "localhost"
MQTT_BROKER_PORT = 1883



def on_message(client, userdata, message):
    if message.topic == "gps":
        gps_operations(message)

    if message.topic == "wifi":
        wifi_operations(message)



client = paho.Client("client-001")

client.on_message = on_message

client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)
client.subscribe("gps")
client.subscribe("wifi")
client.loop_forever()

