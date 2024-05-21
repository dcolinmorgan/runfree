import os
import math
import random
import urllib.parse

import requests
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from flask import Flask, render_template, request
from mapbox import Directions
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
mapbox_token = os.getenv('MAPBOX_TOKEN')
directions = Directions(access_token=mapbox_token)


def geocode_location(location):
    locator = Nominatim(user_agent="runfree")
    location = locator.geocode(location)
    return location.latitude, location.longitude


def find_nearby_destination(start_lat, start_lng, destination_type):
    query = destination_type
    mapbox_token = os.getenv('MAPBOX_TOKEN')
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{query}.json"
    params = {
        'proximity': f'{start_lng},{start_lat}',
        'access_token': mapbox_token
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise ValueError(f"Geocoding request failed with status code {response.status_code}")

    response_json = response.json()

    if 'features' not in response_json:
        raise ValueError("Response does not contain 'features'")

    features = response_json['features']

    if not features:
        raise ValueError(f"No nearby {destination_type} found.")

    closest_feature = None
    closest_distance = float('inf')

    for feature in features:
        destination = feature['geometry']['coordinates']
        destination_coords = (destination[1], destination[0])
        start_coords = (start_lat, start_lng)
        distance = geodesic(start_coords, destination_coords).kilometers

        if distance < closest_distance:
            closest_distance = distance
            closest_feature = feature

    if closest_feature is None:
        raise ValueError(f"No nearby {destination_type} found within a reasonable distance.")

    closest_destination = closest_feature['geometry']['coordinates']
    return closest_destination[1], closest_destination[0]


def generate_trail(start_location, distance=10, unit='km', destination_type=None):
    if unit == 'mi':
        distance *= 1.60934  # Convert miles to kilometers

    start_lat, start_lng = geocode_location(start_location)

    waypoints = []
    total_distance = 0
    prev_waypoint = (start_lng, start_lat)

    num_turns = 0
    while total_distance < distance and num_turns < 4:
        try:
            angle = random.uniform(0, 2 * math.pi)
            radius = random.uniform(0.005, 0.02)
            next_lat = prev_waypoint[1] + radius * math.cos(angle)
            next_lng = prev_waypoint[0] + radius * math.sin(angle)
            next_waypoint = (next_lng, next_lat)

            response = directions.directions([prev_waypoint, next_waypoint], profile='mapbox/walking')
            snapped_waypoint = response.geojson()['features'][0]['geometry']['coordinates'][-1]

            distance_meters = response.geojson()['features'][0]['properties']['distance']

            if total_distance + distance_meters / 1000 > distance:
                break

            waypoints.append(f"{snapped_waypoint[1]},{snapped_waypoint[0]}")
            prev_waypoint = (snapped_waypoint[0], snapped_waypoint[1])
            total_distance += distance_meters / 1000
            num_turns += 1

        except IndexError:
            snapped_waypoint = next_waypoint
            waypoints.append(f"{snapped_waypoint[1]},{snapped_waypoint[0]}")
            prev_waypoint = (snapped_waypoint[0], snapped_waypoint[1])
    if destination_type:
        destination_lat, destination_lng = find_nearby_destination(start_lat, start_lng, destination_type)
        waypoints.append(f"{destination_lat},{destination_lng}")
    waypoints.append(f"{start_lat},{start_lng}")

    start_location_encoded = urllib.parse.quote(start_location)
    waypoints_encoded = "|".join(urllib.parse.quote(wp) for wp in waypoints)

    google_maps_link = f"https://www.google.com/maps/dir/?api=1&origin={start_location_encoded}&destination={start_location_encoded}&waypoints={waypoints_encoded}"

    return google_maps_link,google_maps_link,google_maps_link


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        start_location = request.form['start_location']
        distance = float(request.form['distance'])
        unit = request.form['unit']
        dest = request.form['dest']
        # avoid_ferries = 'avoid_ferries' in request.form
        trail_links = generate_trail(start_location, distance, unit, dest)
        button_names = ["Open Your Route"]
        icon_paths = ["static/icons/GoogleMaps.png"]
        trail_buttons = list(zip(button_names, trail_links, icon_paths))
        return render_template('index.html', trail_buttons=trail_buttons)
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, debug=True)
