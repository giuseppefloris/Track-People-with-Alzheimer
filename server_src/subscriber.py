import paho.mqtt.client as paho
from gps import gps_operations
from bpm import bpm_operations
from wifi import wifi_operations
from accelerometer import acc_operations


MQTT_BROKER_HOST = "localhost"
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

while client.loop() == 0:
    pass


'''
class SensorController:
    def __init__(self, broker_host, broker_port):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client = paho.Client("client-001")
        self.client.on_message = self.on_message

    def on_message(self, client, userdata, message):
        topic_handlers = {
            "gps": gps_operations,
            "bpm": bpm_operations,
            "wifi": wifi_operations,
            "acc": acc_operations
        }

        handler = topic_handlers.get(message.topic)
        if handler:
            handler(message)

    def setup_mqtt(self):
        self.client.connect(self.broker_host, self.broker_port, 60)
        self.client.loop_start()
        self.client.subscribe("gps")
        self.client.subscribe("bpm")
        self.client.subscribe("wifi")
        self.client.subscribe("acc")

    def run(self):
        self.setup_mqtt()
        
        try:
            while True:
                bot_operations()
                time.sleep(1)  # Adjust sleep interval as needed
        except KeyboardInterrupt:
            self.client.disconnect()
            self.client.loop_stop()

if __name__ == "__main__":
    MQTT_BROKER_HOST = "192.168.100.21"
    MQTT_BROKER_PORT = 1883

    sensor_controller = SensorController(MQTT_BROKER_HOST, MQTT_BROKER_PORT)
    sensor_controller.run()
'''
