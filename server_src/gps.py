import folium
import webbrowser
import geopy.distance
from PIL import Image
import io
import os
from wifi import in_out_position
outside_house_cord = False

def retrieve_position():

    with open("gps_data.txt", 'r') as f:
        location = f.read()

    location = str(location)
    location = location.replace("'", '')
    location = location.split(',')
    location = [float(i) for i in location]
    map = folium.Map(location=location, zoom_start=50)
    map.add_child(folium.Marker(location=location, popup='Tughlakabad',
                                icon=folium.Icon(color='green')))

    img_data = map._to_png(5)
    img = Image.open(io.BytesIO(img_data))
    img.save('map.png')
    img = os.path.abspath("map.png")
    webbrowser.open("map.html")
    return img

def gps_operations(msg):

    global outside_house_cord

    print("GPS OPERATIONS\n")
    position = str(msg.payload).replace('b', '')
    print(position)

    if (not outside_house_cord) and (position != "'0.00,0.00'"):
        with open('gps_data_house.txt', 'w') as f:
            f.write(position)
        outside_house_cord = True

    if outside_house_cord and position != "'0.00,0.00'":
        with open('gps_data_house.txt', 'r') as f:
            house_cord = f.read()
            in_out = in_out_position()

            if in_out == 'outside':
                if geofence(house_cord, position):
                    with open('chat_id.txt', 'r') as f:
                        chat_id = f.read()
                        print('OUT OF Geofence')
                        #send(chat_id, 'Out of the safe zone! '
                                      #'Use the /position command to check the current position')



    with open('gps_data.txt', 'w') as f:
        f.write(position)

def geofence(house, current, maximum_distance = 3):
    print('Calculating Geofence')
    house = house.replace("'", '')
    current = current.replace("'", '')
    house = house.split(',')
    current = current.split(',')

    house = [float(i) for i in house]
    current = [float(i) for i in current]

    distance = geopy.distance.geodesic(house, current).m
    if distance > maximum_distance:
        print("Out of the safezone!!")
        return True
    return False

