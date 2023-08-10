import time
import paho.mqtt.client as paho
from bot_code import bot_operations
from gps import gps_operations
from bpm import bpm_operations
from wifi import wifi_operations
from accelerometer import acc_operations


MQTT_BROKER_HOST = "192.168.100.21"
MQTT_BROKER_PORT = 1883


def on_message(client, userdata, message):
    if message.topic == "gps":
        gps_operations(message)

    if message.topic == "bpm":
        bpm_operations(message)

    if message.topic == "wifi":
        wifi_operations(message)

    if message.topic == "acc":
        acc_operations(message)


client = paho.Client("client-001")
client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)
client.on_message = on_message

client.loop_start()
client.subscribe("gps")
client.subscribe("bpm")
client.subscribe("wifi")
client.subscribe("acc")

while True:
    bot_operations()
