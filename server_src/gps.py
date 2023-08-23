import folium
from geopy.distance import geodesic
from flask import  render_template



def create_map(map_center):
    return folium.Map(location=map_center, zoom_start=12)


def map_updates(map_osm, lat, long):
    folium.Marker(location=[lat, long], popup='Received coordinates').add_to(map_osm)
    map_osm.save('templates/map_localization.html')


def index(map_center):
    global map_osm
    if not map_osm:
        map_osm = create_map(map_center)
    map_updates(map_osm, 0, 0)
    return render_template('map_localization.html')


def map_handler(lat, long, ref_lat, ref_lon, max_radius):
    global map_osm
    if map_osm:
        map_updates(map_osm, lat, long)
        current_location = (lat, long)
        reference_location = (ref_lat, ref_lon)
        distance = geodesic(current_location, reference_location).meters

        if distance <= max_radius:
            print("person within the radius")
        else:
            print("person has exceed the distance")


def gps_operations(msg):
    print(msg)
    """
    gps_data = {}
    map_center = [33.4455, 44.5566]
    map_osm = None
    max_radius = 1000
    ref_lat = map_center[0]
    print(ref_lat)
    ref_lon = map_center[1]"""


