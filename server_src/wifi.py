import time, sched
import os
import numpy as np
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder
from datetime import datetime
import pickle
from tinydb import TinyDB, Query

counter = 0


def learn_inside_locations(label, id):
    db = TinyDB('mqtt_database.json')
    clients_table = db.table('clients_table')
    Client = Query()
    client_id = clients_table.search(Client.chat_id==id)

    inside_locations = db.table('inside_locations')
    wifi_table = db.table('wifi_strength_readings')
    _label = Query()
    result = inside_locations.search((_label.client_id == client_id) & (_label.label == label))
    if result:
        return "Label already registered"

    data = []

    # query to retrieve gps data
    wifi_reading = Query()
    for i in range(4):
        wifi_readings = wifi_table.search(wifi_reading.client_id.all==client_id)
        wifi_data = str(wifi_readings[:-1])

        data.append(wifi_data)
        time.sleep(5)

    inside_locations.insert({'client_id': client_id, 'coord_list': data, 'label': label})
    db.close()


def train_model(id):

    print('training the model')
    db = TinyDB('mqtt_database.json')
    clients_table = db.table('clients_table')
    Client = Query()
    client_id = clients_table.search(Client.chat_id==id)

    inside_locations = db.table('inside_locations')
    DataEntry = Query()
    result = inside_locations.search(DataEntry.client_id==client_id)

    data_list = []
    label_list = []

    for entry in result:
        data_list.append(entry['coord_list'])
        label_list.append(entry['label'])

    X = np.array(data_list)
    y = np.array(label_list)
    clf = SVC()
    # y = [i[0] for i in y]
    le = LabelEncoder()
    le.fit(y)
    y = le.transform(y)

    clf.fit(X, y)
    pickle.dump(clf, open('model' + str(client_id) + '.pkl', 'wb'))
    pickle.dump(le, open('label_encoding' +  str(client_id) + '.pkl', 'wb'))
    db.close()


def predict(id):
    db = TinyDB('mqtt_database.json')
    clients_table = db.table('clients_table')
    Client = Query()
    client_id = clients_table.search(Client.chat_id==id)
    inside_locations = db.table('inside_locations')
    wifi_table = db.table('wifi_strength_readings')

    clf = pickle.load(open('model' +  str(client_id) + '.pkl', 'rb'))
    le = pickle.load(open('label_encoding' +  str(client_id) + '.pkl', 'rb'))

    wifi_reading = Query()
    data = []
    for i in range(4):
        wifi_readings = wifi_table.search(wifi_reading.client_id.all==client_id)
        wifi_data = str(wifi_readings[:-1])

        data.append(wifi_data)
        time.sleep(5)

    X_test = np.array(data).reshape((1, 4))
    print(X_test)
    prediction = clf.predict(X_test)
    prediction = le.inverse_transform(prediction)

    DataEntry = Query()

    result = inside_locations.search(DataEntry.client_id==client_id)
    sorted_entries = sorted(result, key=lambda entry: entry.get('prediction_time',
                                                                '1970-01-01 00:00:00'), reverse=True)
    newest_entry = sorted_entries[0] if sorted_entries else None
    newest_label = newest_entry['label'] if newest_entry else None

    if newest_label == prediction:
        t0 = newest_entry['prediction_time']
        t1 = time.time()
        t0 = datetime.fromtimestamp(t0)
        t1 = datetime.fromtimestamp(t1)
        occupancy = t1 - t0
        inside_locations.update({'prediction_time': t1},
                                (DataEntry.client_id == client_id) & (DataEntry.label == prediction))

    else:
        t1 = time.time()
        inside_locations.update({'prediction_time': t1},
                                (DataEntry.client_id == client_id) & (DataEntry.label == prediction))
        occupancy = 'Just Moved'
    db.close()
    return prediction, occupancy


def in_out_position(id):
    db = TinyDB('mqtt_database.json')
    gps_table = db.table('gps_readings')
    wifi_table = db.table('wifi_strength_readings')
    gps_house_coord = db.table('gps_house_coord')

    DataEntry = Query()
    gps_data = gps_table.search(DataEntry.client_id==id)
    h_gps_data = gps_house_coord.search(DataEntry.client_id==id)

    gps_data = gps_data[:-1]
    h_gps_data = h_gps_data[:-1]

    print("in/out computation")

    if gps_data == '0.000000,0.000000':
        position = 'inside'
    else:
        if gps_data == h_gps_data:
            position = 'inside'
        else:
            position = 'outside'
    print(position)
    db.close()
    return position


def wifi_operations(id):
    global counter

    counter += 1

    if counter == 100 and (in_out_position(id) == 'inside'):
        print("Periodical Prediction")
        predict(id)
        counter = 0
