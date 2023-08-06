from flask import Flask, jsonify, render_template
import paho.mqtt.client as mqtt
import json
import gps_conn
from geopy.distance import geodesic
app = Flask(__name__)

# MQTT Settings
MQTT_BROKER_HOST = "your_mqtt_broker_ip"  # Replace with your MQTT broker IP or hostname
MQTT_BROKER_PORT = 1883
MQTT_TOPIC = "gps_data"

# Global variable to store GPS data received from MQTT
gps_data = {}
map_center = [33.4455, 44.5566]
map_osm = None
max_radius = 1000
ref_lat = map_center[0]
print(ref_lat)
ref_lon = map_center[1]
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(MQTT_TOPIC)


def on_message(client, userdata, msg):
    global gps_data
    try:
        payload = msg.payload.decode('utf-8')
        gps_data = parse_gps_data(payload)  # Parse the received GPS data
        userdata['map_handler'](gps_data['latitude'], gps_data['longitude'])
    except Exception as e:
        print("Error processing MQTT message:", e)


def parse_gps_data(payload):
    try:
        parsed_data = json.loads(payload)
        return parsed_data
    except json.JSONDecodeError as e:
        # Handle the case where the payload is not a valid JSON string
        print(f"Error parsing JSON: {e}")
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


def index():
    global map_osm
    if not map_osm:
        map_osm = gps_conn.create_map(map_center)
    gps_conn.map_updates(map_osm, 0, 0)
    return render_template('map_localization.html')


def map_handler(lat, long):
    global map_osm
    if map_osm:
        gps_conn.map_updates(map_osm, lat, long)
        current_location = (lat, long)
        reference_location = (ref_lat, ref_lon)
        distance = geodesic(current_location, reference_location).meters

        if distance <= max_radius:
            print("person within the radius")
        else:
            print("person has exceed the distance")


if __name__ == "__main__":
    client.loop_start()  # Start the MQTT client loop in a separate thread
    app.run(host="0.0.0.0", port=5000)  # Run the Flask app on all available interfaces (0.0.0.0) and port 5000