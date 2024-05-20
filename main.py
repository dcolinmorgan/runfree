import os
import math
import random
import urllib.parse

from flask import Flask, render_template, request
from mapbox import Directions, Geocoder
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
mapbox_token = os.getenv('MAPBOX_TOKEN')
directions = Directions(access_token=mapbox_token)
geocoder = Geocoder(access_token=mapbox_token)


def geocode_location(location):
    response = geocoder.forward(location).geojson()
    coordinates = response['features'][0]['geometry']['coordinates']
    return coordinates[1], coordinates[0]


def find_nearby_destination(start_lat, start_lng, destination_type):
    query = destination_type
    response = geocoder.forward(query, proximity=(start_lng, start_lat)).geojson()
    features = response['features']

    if not features:
        raise ValueError(f"No nearby {destination_type} found.")

    destination = features[0]['geometry']['coordinates']
    return destination[1], destination[0]


def generate_trail(start_location, distance, unit, destination_type):
    if unit == 'mi':
        distance *= 1.60934  # Convert miles to kilometers

    start_lat, start_lng = geocode_location(start_location)

    destination_lat, destination_lng = find_nearby_destination(start_lat, start_lng, destination_type)
    waypoints = []
    total_distance = 0
    prev_waypoint = (start_lng, start_lat)  # Note: Mapbox uses (lng, lat) format

    num_turns = 0  # Track the number of turns
    while total_distance < distance and num_turns < 4:
        try:
            angle = random.uniform(0, 2 * math.pi)
            radius = random.uniform(0.005, 0.02)  # Adjust this radius range as needed
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

    waypoints.append(f"{destination_lat},{destination_lng}")
    waypoints.append(f"{start_lat},{start_lng}")

    start_location_encoded = urllib.parse.quote(start_location)
    waypoints_encoded = "|".join(urllib.parse.quote(wp) for wp in waypoints)

    google_maps_link = f"https://www.google.com/maps/dir/?api=1&origin={start_location_encoded}&destination={start_location_encoded}&waypoints={waypoints_encoded}"
    return google_maps_link


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        start_location = request.form['start_location']
        distance = float(request.form['distance'])
        unit = request.form['unit']
        run_to = request.form['run_to']
        # avoid_ferries = 'avoid_ferries' in request.form
        trail_links = generate_trail(start_location, distance, unit, run_to)
        button_names = "GoogleMaps"
        icon_paths = "static/icons/GoogleMaps.png"
        trail_buttons = list(zip(button_names, trail_links, icon_paths))
        return render_template('index.html', trail_buttons=trail_buttons)
    return render_template('index.html')


# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8110)
