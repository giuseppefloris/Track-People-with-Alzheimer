from flask import Flask, jsonify
import paho.mqtt.client as mqtt

app = Flask(__name__)

# MQTT Settings
MQTT_BROKER_HOST = "your_mqtt_broker_ip"  # Replace with your MQTT broker IP or hostname
MQTT_BROKER_PORT = 1883
MQTT_TOPIC = "gps_data"

# Global variable to store GPS data received from MQTT
gps_data = {}


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(MQTT_TOPIC)


def on_message(client, userdata, msg):
    global gps_data
    try:
        payload = msg.payload.decode()
        gps_data = parse_gps_data(payload)  # Parse the received GPS data
    except Exception as e:
        print("Error processing MQTT message:", e)


def parse_gps_data(payload):
    # Implement your GPS data parsing logic here based on the payload format
    # For example, if your payload is a JSON string:
    # parsed_data = json.loads(payload)
    # return parsed_data

    # Replace the following line with your parsing logic based on the actual payload format
    return {}


# MQTT client setup
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)


@app.route("/gps")
def get_gps_data():
    return jsonify(gps_data)


if __name__ == "__main__":
    client.loop_start()  # Start the MQTT client loop in a separate thread
    app.run(host="0.0.0.0", port=5000)  # Run the Flask app on all available interfaces (0.0.0.0) and port 5000