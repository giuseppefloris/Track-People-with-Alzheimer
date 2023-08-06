import folium


def create_map(map_center):
    return folium.Map(location=map_center, zoom_start=12)


def map_updates(map_osm, lat, long):
    folium.Marker(location=[lat, long], popup='Received coordinates').add_to(map_osm)
    map_osm.save('templates/map_localization.html')
