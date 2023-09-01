import paho.mqtt.client as paho
from gps import gps_operations
from wifi import wifi_operations
from tinydb import TinyDB, Query

MQTT_BROKER_HOST = "localhost"
MQTT_BROKER_PORT = 1883


# id = 164181 secret = gAAAAABk7Sh


def on_message(client, userdata, message):
    message_topics = message.topic.split('/')
    topic = message_topics[2]
    clnt_id = message_topics[1]

    db = TinyDB('mqtt_database.json')
    clients_table = db.table('clients')
    existent_client = Query()
    result = clients_table.search(existent_client.client_id == clnt_id)
    if not result:
        clients_table.insert({'client_id': clnt_id, 'chat_id': '', 'auth': False, 'setup': False,
                              'train': False, 'count': 0,'count_max': False, 'OOS': False, 'geofence': False})

    if topic == "gps":
        message = str(message.payload)
        message = message.replace("b", "")
        message = message.replace("'", "")
        print('client_id', clnt_id, 'coord', message)
        gps_table.insert({'client_id': clnt_id, 'coord': message})
        gps_operations(clnt_id)

    if topic == "wifi":
        message = str(message.payload)
        message = message.replace("b", "")
        message = message.replace("'", "")
        print('client_id', clnt_id, 'wifi_s', message)
        wifi_table.insert({'client_id': clnt_id, 'wifi_s': message})
        wifi_operations(clnt_id)

    db.close()


db = TinyDB('mqtt_database.json')
clients_table = db.table('clients')
gps_table = db.table('gps_readings')
wifi_table = db.table('wifi_strength_readings')
gps_house_coord = db.table('gps_house_coord')
inside_locations = db.table('inside_locations')


client = paho.Client("Server")
client.on_message = on_message
client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)
client.subscribe("Device/#")
client.loop_forever()
