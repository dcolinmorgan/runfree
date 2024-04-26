from flask import Flask, render_template, request
# import googlemaps
from mapbox import Directions
import os
import math
import random
import urllib.parse
import geopy.distance
from geopy.geocoders import Nominatim
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
# gmap_key = os.getenv('gmap_key')
# gmaps = googlemaps.Client(key=gmap_key)
# Initialize Mapbox client
mapbox_token = os.getenv('MAPBOX_TOKEN')
directions = Directions(access_token=mapbox_token)

# the idea is to break the total distance into between 2-6 segments,
# each of which will be defined by only 2 waypoints, and all of which
# then combined into the total distance, beginning and ending at the
# same user defined location


def generate_trail(start_location, distance, unit):
  if unit == 'mi':
    distance *= 1.60934  # Convert miles to kilometers

  # Geocode the starting location
  start_lat, start_lng = geocode_location(start_location)

  # Generate random waypoints for the trail
  waypoints = []
  total_distance = 0
  prev_waypoint = (start_lng, start_lat)  # Note: Mapbox uses (lng, lat) format

  num_turns = 0  # Track the number of turns
  while total_distance < distance and num_turns < 4:
    try:
      # Generate a random next waypoint with a circular bias
      angle = random.uniform(0, 2 * math.pi)
      radius = random.uniform(0.005,
                              0.02)  # Adjust this radius range as needed
      next_lat = prev_waypoint[1] + radius * math.cos(angle)
      next_lng = prev_waypoint[0] + radius * math.sin(angle)
      next_waypoint = (next_lng, next_lat)

      # Snap the next waypoint to roads
      response = directions.directions([prev_waypoint, next_waypoint],
                                       profile='mapbox/walking')
      snapped_waypoint = response.geojson(
      )['features'][0]['geometry']['coordinates'][-1]

      # Calculate the distance between the previous and current waypoints
      distance_meters = response.geojson(
      )['features'][0]['properties']['distance']

      # Check if adding the segment distance exceeds the desired total distance
      if total_distance + distance_meters / 1000 > distance:
        break

      # Append the snapped waypoint to the trail
      waypoints.append(f"{snapped_waypoint[1]},{snapped_waypoint[0]}")
      prev_waypoint = (snapped_waypoint[0], snapped_waypoint[1]
                       )  # Note: Mapbox uses (lng, lat) format
      total_distance += distance_meters / 1000

      # Count the number of turns
      num_turns += 1

    except IndexError:
      # If no snapped waypoint is found, use the original next waypoint
      snapped_waypoint = next_waypoint
      waypoints.append(f"{snapped_waypoint[1]},{snapped_waypoint[0]}")
      prev_waypoint = (snapped_waypoint[0], snapped_waypoint[1]
                       )  # Note: Mapbox uses (lng, lat) format

  # Ensure the start and end locations are the same
  waypoints.append(f"{start_lat},{start_lng}")

  # URL-encode the start location and waypoints
  start_location_encoded = urllib.parse.quote(start_location)
  waypoints_encoded = "|".join(urllib.parse.quote(wp) for wp in waypoints)

  # Create the Mapbox link with generated waypoints
  mapbox_link = f"https://www.mapbox.com/directions?origin={start_location_encoded}&destination={start_location_encoded}&waypoints={waypoints_encoded}"

  # Create links for other maps
  google_maps_link = f"https://www.google.com/maps/dir/?api=1&origin={start_location_encoded}&destination={start_location_encoded}&waypoints={waypoints_encoded}"
  apple_maps_link = f"http://maps.apple.com/?saddr={start_location_encoded}&daddr={start_location_encoded}&dirflg=w&wp={waypoints_encoded}"
  openstreetmap_link = f"https://www.openstreetmap.org/directions?engine=graphhopper_foot&route={start_location_encoded}%3B{start_location_encoded}&route={waypoints_encoded}"

  return google_maps_link, apple_maps_link, openstreetmap_link


def geocode_location(location):
  # Use geopy for geocoding
  locator = Nominatim(user_agent="runfree")
  location = locator.geocode(location)
  return location.latitude, location.longitude


@app.route('/', methods=['GET', 'POST'])
def index():
  if request.method == 'POST':
    start_location = request.form['start_location']
    distance = float(request.form['distance'])
    unit = request.form['unit']
    # avoid_ferries = 'avoid_ferries' in request.form
    trail_links = generate_trail(start_location, distance, unit)
    button_names = ["GoogleMaps", "AppleMaps", "OpenStreetMaps"]
    icon_paths = [
        "static/icons/GoogleMaps.png", "static/icons/AppleMaps.png",
        "static/icons/OpenStreetMaps.png"
    ]
    trail_buttons = list(zip(button_names, trail_links, icon_paths))
    return render_template('index.html', trail_buttons=trail_buttons)
  return render_template('index.html')


# Run the Flask app
if __name__ == '__main__':
  app.run(host='0.0.0.0', port=82)
