from flask import Flask, render_template, request
import googlemaps
import os
import math
import random
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
gmap_key = os.getenv('gmap_key')
gmaps = googlemaps.Client(key=gmap_key)

# the idea is to break the total distance into between 2-6 segments,
# each of which will be defined by only 2 waypoints, and all of which
# then combined into the total distance, beginning and ending at the
# same user defined location
import googlemaps
import random
import urllib.parse


def generate_trail(start_location, distance, unit, avoid_ferries):
  if unit == 'mi':
    distance *= 1.60934  # Convert miles to kilometers

  # Geocode the starting location to get latitude and longitude
  geocode_result = gmaps.geocode(start_location)
  start_lat = geocode_result[0]['geometry']['location']['lat']
  start_lng = geocode_result[0]['geometry']['location']['lng']

  # Find nearby parks using Google Places API
  places_result = gmaps.places_nearby(
      location=(start_lat, start_lng),
      radius=5000,  # Search within a 10km radius
      type='park')

  # Extract parks and format them as waypoints
  park_waypoints = [
      f"{place['geometry']['location']['lat']},{place['geometry']['location']['lng']}"
      for place in places_result['results']
  ]

  # Check if there are at least one park, if not, handle the scenario
  if not park_waypoints:
    print("No parks found within a 10km radius.")
    return None

  # Create a route that includes the parks as waypoints
  waypoints_encoded = "|".join(urllib.parse.quote(wp) for wp in park_waypoints)

  # URL-encode the start location
  start_location_encoded = urllib.parse.quote(start_location)

  # Create the Google Maps link with generated waypoints
  google_maps_link = f"https://www.google.com/maps/dir/?api=1&origin={start_location_encoded}&destination={start_location_encoded}&waypoints={waypoints_encoded}"

  return google_maps_link


@app.route('/', methods=['GET', 'POST'])
def index():
  if request.method == 'POST':
    start_location = request.form['start_location']
    distance = float(request.form['distance'])
    unit = request.form['unit']
    avoid_ferries = 'avoid_ferries' in request.form
    trail_link = generate_trail(start_location, distance, unit, avoid_ferries)
    return render_template('index.html', trail_link=trail_link)
  return render_template('index.html')


# Run the Flask app
if __name__ == '__main__':
  app.run(host='0.0.0.0', port=82)
