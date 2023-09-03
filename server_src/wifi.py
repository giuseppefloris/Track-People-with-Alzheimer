import time
import os
import numpy as np
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder
import pickle
from tinydb import TinyDB, Query
from datetime import datetime


def learn_inside_locations(lbl, id):
    print('learn inside locations')
    db = TinyDB('mqtt_database.json')
    clients_table = db.table('clients')
    inside_locations = db.table('inside_locations')

    Client = Query()
    client = clients_table.search(Client.chat_id == id)
    client = client[0]
    client = client['client_id']
    print(client)
    labels = Query()
    result = inside_locations.search((labels.client_id == client) & (labels.label == lbl))
    db.close()

    if len(result) != 0:
        result = result[0]
        if result['label'] == lbl:
            return "Label already registered"

    data = []

    for i in range(4):
        db = TinyDB('mqtt_database.json')
        wifi_table = db.table('wifi_strength_readings')
        wifi_reading = Query()
        wifi_readings = wifi_table.search(wifi_reading.client_id.all(client))
        wifi_data = wifi_readings[-1]

        wifi_data = wifi_data['wifi_s']
        data.append(wifi_data)
        print(data)
        db.close()
        time.sleep(4)

    db = TinyDB('mqtt_database.json')
    inside_locations = db.table('inside_locations')
    inside_locations.insert({'client_id': client, 'coord_list': data, 'label': lbl})
    db.close()
    return "Move to the next location or exit setup with /position command"


def train_model(id):
    print('training the model')
    db = TinyDB('mqtt_database.json')
    clients_table = db.table('clients')
    Client = Query()
    client = clients_table.search(Client.chat_id == id)
    client = client[0]
    client = client['client_id']

    inside_locations = db.table('inside_locations')
    DataEntry = Query()
    result = inside_locations.search(DataEntry.client_id == client)

    data_list = []
    label_list = []

    for entry in result:
        data_list.append(entry['coord_list'])
        label_list.append(entry['label'])

    print(data_list)
    print(label_list)

    X = np.array(data_list)
    y = np.array(label_list)
    clf = SVC()
    # y = [i[0] for i in y]
    le = LabelEncoder()
    le.fit(y)
    y = le.transform(y)
    X = X.reshape(-1, 4)
    print(X)
    clf.fit(X, y)
    pickle.dump(clf, open('model' + str(client) + '.pkl', 'wb'))
    pickle.dump(le, open('label_encoding' + str(client) + '.pkl', 'wb'))
    db.close()


def predict(client, periodical=False):
    print('Predicting')
    if not periodical:
        db = TinyDB('mqtt_database.json')
        clients_table = db.table('clients')
        Client = Query()
        client = clients_table.search(Client.chat_id == client)
        client = client[0]
        client = client['client_id']
        db.close()

    clf = pickle.load(open('model' + str(client) + '.pkl', 'rb'))
    le = pickle.load(open('label_encoding' + str(client) + '.pkl', 'rb'))

    data = []
    for i in range(4):
        db = TinyDB('mqtt_database.json')
        wifi_table = db.table('wifi_strength_readings')
        wifi_reading = Query()
        wifi_readings = wifi_table.search(wifi_reading.client_id.all(client))
        wifi_data = wifi_readings[-1]

        wifi_data = wifi_data['wifi_s']
        data.append(wifi_data)
        print(data)
        db.close()
        time.sleep(4)

    X_test = np.array(data).reshape((1, 4))
    print(X_test)
    prediction = clf.predict(X_test)
    prediction = le.inverse_transform(prediction)

    occupancy = 0
    db = TinyDB('mqtt_database.json')
    inside_locations = db.table('inside_locations')
    last_position = Query()
    flag = inside_locations.search((last_position.client_id == client) & (last_position.flag == 1))
    print(flag)

    if len(flag) == 0:
        print('adding first flag')
        t = time.time()
        inside_locations.update({'flag': 1, 'prediction_time': t},
                                (last_position.client_id == client) & (last_position.label == prediction[0]))
        occupancy = 'Just Moved'

    if len(flag) != 0:
        flag = flag[0]
        print('checking the flags label')
        if flag['label'] == prediction:
            print('same place')
            t0 = flag['prediction_time']
            t1 = time.time()
            t0 = datetime.fromtimestamp(t0)
            print(t0)
            t1 = datetime.fromtimestamp(t1)
            print(t1)
            occupancy = t1 - t0

        else:
            print('different place')
            inside_locations.update({'flag': 0},
                                    (last_position.client_id == client) & (last_position.label == flag['label']))
            t = time.time()
            inside_locations.update({'flag': 1, 'prediction_time': t},
                                    (last_position.client_id == client) & (last_position.label == prediction[0]))
            occupancy = 'Just Moved'

    db.close()

    return prediction, occupancy


def in_out_position(id):
    print("in/out computation")

    db = TinyDB('mqtt_database.json')
    gps_table = db.table('gps_readings')
    gps_house_coord = db.table('gps_house_coord')

    DataEntry = Query()
    gps_data = gps_table.search(DataEntry.client_id == id)
    h_gps_data = gps_house_coord.search(DataEntry.client_id == id)

    gps_data = gps_data[-1]
    if len(h_gps_data) != 0:
        h_gps_data = h_gps_data[-1]

    if gps_data['coord'] == '0.000000,0.000000':
        position = 'inside'
    else:
        if (len(h_gps_data) != 0) and (gps_data['coord'] == h_gps_data['coord']):
            position = 'inside'
        else:
            position = 'outside'
    print(position)
    db.close()
    return position


def wifi_operations(id):
    db = TinyDB('mqtt_database.json')
    clients_table = db.table('clients')
    Client = Query()
    client = clients_table.search(Client.client_id == id)
    client = client[0]
    count = client['count']

    if not client['count_max']:
        max_count = 100
    else:
        max_count = client['count_max']

    count += 1
    clients_table.update({'count': count}, (Client.client_id == id))
    db.close()

    trained = os.path.exists('model' + str(id) + '.pkl')

    if trained and count == max_count and (in_out_position(id) == 'inside'):
        print("Periodical Prediction")
        prediction, occupancy = predict(id, periodical=True)
        print('prediction', prediction, 'occupancy', occupancy)
        db = TinyDB('mqtt_database.json')
        clients_table = db.table('clients')
        Client = Query()
        clients_table.update({'count': 0}, (Client.client_id == id))
        db.close()
