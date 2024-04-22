from flask import Flask, render_template, request
import googlemaps
import os
import random
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
gmap_key = os.getenv('gmap_key')
gmaps = googlemaps.Client(key=gmap_key)


def generate_trail(start_location, distance, unit, avoid_highways,
                   avoid_bridges):
  if unit == 'mi':
    distance *= 1.60934  # Convert miles to kilometers

  # Geocode the starting location
  geocode_result = gmaps.geocode(start_location)
  start_lat = geocode_result[0]['geometry']['location']['lat']
  start_lng = geocode_result[0]['geometry']['location']['lng']

  # Generate random waypoints for the trail
  waypoints = []
  remaining_distance = distance * 1000
  prev_waypoint = (start_lat, start_lng)

  while remaining_distance > 0:
    try:
      # Generate a random next waypoint
      next_waypoint = (prev_waypoint[0] + random.uniform(-0.01, 0.01),
                       prev_waypoint[1] + random.uniform(-0.01, 0.01))

      # Snap the next waypoint to roads
      snapped_waypoint = gmaps.snap_to_roads([next_waypoint],
                                             interpolate=True)[0]

      # Calculate the distance between the previous and current waypoints
      distance_result = gmaps.distance_matrix(
          origins=f"{prev_waypoint[0]},{prev_waypoint[1]}",
          destinations=
          f"{snapped_waypoint['location']['latitude']},{snapped_waypoint['location']['longitude']}",
          mode="walking",
          avoid=','.join(
              filter(None, [
                  'highways' if avoid_highways else None,
                  'bridges' if avoid_bridges else None
              ])))
      distance_meters = distance_result['rows'][0]['elements'][0]['distance'][
          'value']

      # Check if adding the waypoint exceeds the desired distance
      if remaining_distance - distance_meters <= 0:
        break

      waypoints.append(
          f"{snapped_waypoint['location']['latitude']},{snapped_waypoint['location']['longitude']}"
      )
      prev_waypoint = (snapped_waypoint['location']['latitude'],
                       snapped_waypoint['location']['longitude'])
      remaining_distance -= distance_meters

    except IndexError:
      # If no snapped waypoint is found, use the original next waypoint
      snapped_waypoint = next_waypoint
      waypoints.append(f"{snapped_waypoint[0]},{snapped_waypoint[1]}")
      prev_waypoint = (snapped_waypoint[0], snapped_waypoint[1])
      remaining_distance = 0  # Stop the loop if no snapped waypoint found

  # Ensure the start and end locations are the same
  waypoints.append(f"{start_lat},{start_lng}")

  # URL-encode the start location and waypoints
  start_location_encoded = urllib.parse.quote(start_location)
  waypoints_encoded = "|".join(urllib.parse.quote(wp) for wp in waypoints)

  # Create the Google Maps link with generated waypoints
  google_maps_link = f"https://www.google.com/maps/dir/?api=1&origin={start_location_encoded}&destination={start_location_encoded}&waypoints={waypoints_encoded}"

  return google_maps_link


@app.route('/', methods=['GET', 'POST'])
def index():
  if request.method == 'POST':
    start_location = request.form['start_location']
    distance = float(request.form['distance'])
    unit = request.form['unit']
    avoid_highways = 'avoid_highways' in request.form
    avoid_bridges = 'avoid_bridges' in request.form
    trail_link = generate_trail(start_location, distance, unit, avoid_highways,
                                avoid_bridges)
    return render_template('index.html', trail_link=trail_link)
  return render_template('index.html')


if __name__ == '__main__':
  app.run(debug=True)
