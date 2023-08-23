"""
Publish some messages to queue
"""
import paho.mqtt.publish as publish


msgs = [{'topic': "gps", 'payload': "jump"},
        {'topic': "bpm", 'payload': "some photo"},
        {'topic': "wifi", 'payload': "extra extra"},
        {'topic': "acc", 'payload': "super extra"}]

host = "localhost"


if __name__ == '__main__':
    # publish a single message
    publish.single(topic="kids/yolo", payload="just do it", hostname=host)

    # publish multiple messages
    publish.multiple(msgs, hostname=host)
