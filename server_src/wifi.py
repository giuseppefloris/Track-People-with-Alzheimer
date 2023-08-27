import time, sched
import os
import numpy as np
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder
from datetime import datetime
import pickle

predicted = False
def learn_inside_locations(label):

    data = []
    label_list = []
    if not os.path.exists('X.pkl'):
        pickle.dump(np.array(data), open('X.pkl', 'wb'))
        pickle.dump(np.array(label_list), open('y.pkl', 'wb'))

    for i in range(4):

        with open('wifi_data.txt') as f:
            wifi_data = f.read()
            f.close()
        wifi_data = wifi_data.replace("b", "")
        data.append(wifi_data)
        time.sleep(5)
    X = pickle.load(open('X.pkl', 'rb'))
    y = pickle.load(open('y.pkl', 'rb'))
    if X.shape[0] == 0:
        X = np.array(data, dtype=int)
        y = np.array(label)
    else:
        X = np.vstack((X, np.array(data)))
        y = np.hstack((y, np.array(label)))

    pickle.dump(X, open('X.pkl', 'wb'))
    pickle.dump(y, open('y.pkl', 'wb'))
    print(X)
    print(y)

def train_model():
    with open('predicted_labels', 'w') as f:
        t = time.time()
        f.write(f'{time}'+ ' - label')
        f.close()

    print('training the model')
    X = pickle.load(open('X.pkl', 'rb'))
    y = pickle.load(open('y.pkl', 'rb'))
    clf = SVC()


    # y = [i[0] for i in y]
    le = LabelEncoder()
    le.fit(y)
    y = le.transform(y)

    clf.fit(X, y)
    pickle.dump(clf, open('model.pkl', 'wb'))
    pickle.dump(le, open('label_encoding.pkl', 'wb'))



def predict():
    global predicted

    predicted = True
    clf = pickle.load(open('model.pkl', 'rb'))
    le = pickle.load(open('label_encoding.pkl', 'rb'))
    data = []
    for i in range(4):
        with open('wifi_data.txt') as f:
            wifi_data = f.read()
            f.close()
        wifi_data = wifi_data.replace("b", "")
        data.append(wifi_data)
        time.sleep(5)


    X_test = np.array(data).reshape((1,4))
    prediction = clf.predict(X_test)

    prediction = le.inverse_transform(prediction)
    with open('predicted_labels', 'rw') as f:
        previous_label = f.read()
        previous_label = previous_label.split('-')
        if previous_label[1] != prediction:
            t = time.time()
            f.write(f'{time}' + f' - {prediction}')
            occupancy = ' - '
        else:
            previous_time = float(previous_label[0])
            t = time.time()
            timestamp = t - previous_time
            occupancy = datetime.fromtimestamp(timestamp)


    return prediction, occupancy



def in_out_position():
    print("in out computation")
    with open('gps_data.txt', 'rb') as f:
        gps = f.read()
    with open('wifi_data.txt') as f:
        wifi_data = f.read()
    gps = str(gps)
    gps = gps.replace("b", "")
    gps = gps.replace("-", "")
    wifi_data = str(wifi_data)
    wifi_data = wifi_data.replace("b", "")
    wifi_data = wifi_data.replace("-", "")
    wifi_data = wifi_data.replace("'", "")
    wifi_data = int(wifi_data)

    if gps == '0.00,0.00':
        position = 'inside'
    else:
        if wifi_data < 80:
            position = 'inside'
        else:
            position = 'outside'
    print(position)
    return position


def wifi_operations(msg):
    print('WIFI OPERATIONS')
    print(msg.payload)
    with open('wifi_data.txt', 'wb') as f:
        f.write(msg.payload)
        f.close()


s = sched.scheduler(time.time, time.sleep)
def periodical_prediction(sc):
    print('Periodical Prediction')
    predict()
    sc.enter(120, 1, periodical_prediction, (sc,))

s.enter(120, 1, periodical_prediction, (s,))

if predicted:
    s.run()
