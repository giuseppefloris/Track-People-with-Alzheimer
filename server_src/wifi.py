from whereami import learn
from whereami import get_pipeline
from whereami import predict, predict_proba, crossval, locations




def wifi_operations(msg):
    print(msg.payload)
    with open('wifi_data.txt', 'wb') as f:
        f.write(msg.payload)

