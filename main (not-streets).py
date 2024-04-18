from flask import Flask, request, render_template, redirect, url_for, send_file
import os
import shutil
import random
from geopy.distance import distance
from geopy.point import Point
from geopy.geocoders import Nominatim
import folium

app = Flask(__name__)
# app.secret_key = 'your_secret_key'  # Replace this with a secure secret key

# Define paths
TEMPLATE_MAP_FILE = 'templates/trail_map.html'
STATIC_MAP_FILE = 'static/trail_map.html'


# Function to copy the file from static/ to templates/ on GET request
def copy_trail_map():
  if os.path.exists(STATIC_MAP_FILE):
    shutil.copy(STATIC_MAP_FILE, TEMPLATE_MAP_FILE)


# Helper function to generate a random trail
def generate_random_trail(starting_point,
                          total_distance_km,
                          segment_length_km=0.5):
  trail_points = [starting_point]
  current_point = Point(starting_point)
  total_distance_covered = 0

  while total_distance_covered < total_distance_km:
    # Random angle (bearing) between 0 and 360 degrees
    angle = random.uniform(0, 360)

    # Create a distance object for the segment length
    segment_distance = distance(kilometers=segment_length_km)

    # Calculate the next point
    next_point = segment_distance.destination(current_point, angle)

    # Add next point to trail
    trail_points.append((next_point.latitude, next_point.longitude))

    # Update current point and distance covered
    current_point = next_point
    total_distance_covered += segment_length_km

  return trail_points


# Route for the main page
@app.route('/', methods=['GET', 'POST'])
def index():
  # Copy the trail map file on GET request
  if request.method == 'GET':
    copy_trail_map()

  if request.method == 'POST':
    # Get the user inputs
    starting_address = request.form.get('starting_address')
    total_distance_km = float(request.form.get('total_distance'))

    # Geocode the starting address to get latitude and longitude
    geolocator = Nominatim(user_agent="random_trail_generator")
    location = geolocator.geocode(starting_address)
    if location is None:
      return render_template('index.html',
                             error="Address not found. Please try again.")

    starting_point = (location.latitude, location.longitude)

    # Generate a random trail
    trail_points = generate_random_trail(starting_point, total_distance_km)

    # Create a map with Folium
    m = folium.Map(location=starting_point, zoom_start=14)
    folium.PolyLine(trail_points, color='blue', weight=2.5,
                    opacity=1).add_to(m)
    folium.Marker(starting_point, popup='Starting Point').add_to(m)

    # Save the map as an HTML file in static/ folder
    m.save(STATIC_MAP_FILE)

    # Render the trail_map.html template to display the map
    return render_template('trail_map.html', map_file=STATIC_MAP_FILE)

  # Render the index.html template for GET requests
  return render_template('index.html')


# Run the app on the default port (80)
if __name__ == '__main__':
  app.run(host='0.0.0.0', port=80)
