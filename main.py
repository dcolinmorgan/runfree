import os
import random
import shutil

import folium
import gpxpy
import gpxpy.gpx
import requests
from flask import Flask, render_template, request
from geopy.distance import geodesic
from geopy.geocoders import Nominatim

app = Flask(__name__)
app.secret_key = os.environ['STRAVA_CS']

# Define paths
TEMPLATE_MAP_FILE = 'templates/trail_map.html'
STATIC_MAP_FILE = 'static/trail_map.html'
gpx_file_path = 'static/trail_map.gpx'

# Define the OSRM API base URL
OSRM_BASE_URL = "http://router.project-osrm.org/route/v1/driving"


# Function to copy the file from static/ to templates/ on GET request
def copy_trail_map():
  if os.path.exists(STATIC_MAP_FILE):
    shutil.copy(STATIC_MAP_FILE, TEMPLATE_MAP_FILE)


# Helper function to calculate distance in meters
def calculate_route_distance(route):
  return sum(geodesic(route[i], route[i + 1]).m for i in range(len(route) - 1))


# Function to generate random trail following the streets
def generate_random_trail_following_streets(starting_point, total_distance_km):
  total_distance_m = total_distance_km * 1000
  trail_points = [starting_point]
  current_point = starting_point
  total_distance_covered = 0

  # Loop to generate trail points until the total distance is reached
  while total_distance_covered < total_distance_m:
    # Choose a random angle and distance for the next segment
    angle = random.uniform(0, 360)
    segment_length_m = random.uniform(500,
                                      1000)  # Random segment length in meters

    # Calculate the next point
    next_point = geodesic(meters=segment_length_m).destination(
        current_point, angle)

    # Get the route from the current point to the next point using OSRM API
    coordinates = f"{current_point[1]},{current_point[0]};{next_point.longitude},{next_point.latitude}"
    response = requests.get(
        f"{OSRM_BASE_URL}/{coordinates}?overview=full&geometries=geojson")

    # Check if the API request was successful
    if response.status_code == 200:
      data = response.json()
      if data["code"] == "Ok":
        # Get the route points
        route_points = data["routes"][0]["geometry"]["coordinates"]

        # Convert the coordinates to (latitude, longitude)
        route_points = [(point[1], point[0]) for point in route_points]

        # Calculate the distance of the route
        route_distance = calculate_route_distance(route_points)

        # Add the route points to the trail
        trail_points += route_points[
            1:]  # Exclude the first point as it is the current point

        # Update the current point and total distance covered
        current_point = route_points[-1]
        total_distance_covered += route_distance

    # If the API request failed, break the loop
    else:
      break

  return trail_points


def export_to_gpx(trail_points, filename):
  # Create a new GPX file
  gpx = gpxpy.gpx.GPX()

  # Create a new GPX track
  gpx_track = gpxpy.gpx.GPXTrack()
  gpx.tracks.append(gpx_track)

  # Create a new segment in the track
  gpx_segment = gpxpy.gpx.GPXTrackSegment()
  gpx_track.segments.append(gpx_segment)

  # Add trail points to the GPX segment
  for point in trail_points:
    gpx_segment.points.append(
        gpxpy.gpx.GPXTrackPoint(latitude=point[0], longitude=point[1]))

  # Save the GPX file
  with open(filename, 'w') as gpx_file:
    gpx_file.write(gpx.to_xml())

  return filename


def upload_to_strava(gpx_file_path, access_token):
  # URL for uploading activities
  url = 'https://www.strava.com/api/v3/uploads'

  # Prepare the file for upload
  with open(gpx_file_path, 'rb') as gpx_file:
    files = {'file': gpx_file}
    data = {'data_type': 'gpx'}

    # Make the request to upload the file
    headers = {'Authorization': f'Bearer {app.secret_key}'}
    response = requests.post(url, headers=headers, files=files, data=data)

  # Handle response
  if response.status_code == 201:
    return "Upload successful"
  else:
    return f"Upload failed: {response.text}"


@app.route('/upload_to_strava', methods=['POST'])
def upload_to_strava_route():
  gpx_file_path = request.form.get('gpx_file')
  access_token = app.secret_key

  # Call the function to upload the GPX file to Strava
  result = upload_to_strava(gpx_file_path, access_token)

  # Return the result of the upload
  return result


@app.route('/', methods=['GET', 'POST'])
def index():
  # Copy the trail map file on GET request
  # if request.method == 'GET':
  #   copy_trail_map()
  if request.method == 'POST':
    # Get user input from the form
    starting_address = request.form.get('starting_address')
    total_distance_km = float(request.form.get('total_distance'))

    # Convert starting address to coordinates
    geolocator = Nominatim(user_agent="trail_generator")
    location = geolocator.geocode(starting_address)
    if location is None:
      return render_template('index.html',
                             error="Address not found. Please try again.")

    starting_point = (location.latitude, location.longitude)

    # Generate a random trail following the streets
    trail_points = generate_random_trail_following_streets(
        starting_point, total_distance_km)

    # Create a folium map
    m = folium.Map(location=starting_point, zoom_start=14)
    folium.PolyLine(trail_points, color='blue', weight=3).add_to(m)
    folium.Marker(starting_point, popup="Starting Point").add_to(m)

    # Export trail to GPX format
    gpx_filename = 'static/trail_map.gpx'
    export_to_gpx(trail_points, gpx_filename)

    # Save the map to the file
    m.save(TEMPLATE_MAP_FILE)

    # Render the trail map template
    return render_template('trail_map.html',
                           map_file=TEMPLATE_MAP_FILE,
                           gpx_file=gpx_filename)

  # On GET request, render the index.html
  return render_template('index.html')


# Run the Flask app
if __name__ == '__main__':
  # app.debug = True  # Enable debug mode
  app.run(host='0.0.0.0')  # , port=80)
