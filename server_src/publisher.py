"""
Publish some messages to queue
"""
import paho.mqtt.publish as publish


msgs = [{'topic': "gps", 'payload': "sto in messicooooo"},
        {'topic': "bpm", 'payload': "3500"},
        {'topic': "wifi", 'payload': "-23db"},
        {'topic': "acc", 'payload': "sto cadendoooo"}]

host = "localhost"


if __name__ == '__main__':
    # publish a single message
    #publish.single(topic="kids/yolo", payload="just do it", hostname=host)

    # publish multiple messages
    publish.multiple(msgs, hostname=host)
