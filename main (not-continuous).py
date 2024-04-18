from flask import Flask, render_template, request
import os, shutil, random, requests, folium
from geopy.geocoders import Nominatim
from geopy.distance import distance
from geopy.point import Point

app = Flask(__name__)
# app.secret_key = 'your_secret_key'  # Replace this with a secure secret key

# Define paths
TEMPLATE_MAP_FILE = 'templates/trail_map.html'
STATIC_MAP_FILE = 'static/trail_map.html'


# Function to copy the file from static/ to templates/ on GET request
def copy_trail_map():
  if os.path.exists(STATIC_MAP_FILE):
    shutil.copy(STATIC_MAP_FILE, TEMPLATE_MAP_FILE)


# Helper function to generate random trails that follow the streets
def generate_random_trail_following_streets(starting_point, total_distance_km):
  # OSRM API base URL
  osrm_base_url = "http://router.project-osrm.org/route/v1/driving"

  # Create a list to store trail points
  trail_points = [starting_point]

  # Calculate the total distance in meters
  total_distance_m = total_distance_km * 1000

  # Current point and total distance covered
  current_point = Point(starting_point)
  total_distance_covered = 0

  # Loop until the total distance covered reaches the desired distance
  while total_distance_covered < total_distance_m:
    # Choose a random angle and distance
    angle = random.uniform(0, 360)
    segment_length_m = random.uniform(200,
                                      500)  # Length of each segment in meters

    # Calculate the next point using geopy
    segment_distance = distance(meters=segment_length_m)
    next_point = segment_distance.destination(current_point, angle)

    # Call OSRM API to find the route following the streets
    coordinates = f"{current_point.longitude},{current_point.latitude};{next_point.longitude},{next_point.latitude}"
    response = requests.get(
        f"{osrm_base_url}/{coordinates}?overview=full&geometries=geojson")

    # Check if the request was successful
    if response.status_code == 200:
      data = response.json()
      if data["code"] == "Ok":
        # Add the street-following route points to the trail
        route_points = data["routes"][0]["geometry"]["coordinates"]
        for coord in route_points:
          trail_points.append((coord[1], coord[0]))

        # Update current point and total distance covered
        current_point = Point(route_points[-1][1], route_points[-1][0])
        total_distance_covered += segment_length_m

    # If the request failed, break the loop
    else:
      break

  return trail_points


@app.route('/', methods=['GET', 'POST'])
def index():
  # Copy the trail map file on GET request
  if request.method == 'GET':
    copy_trail_map()
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

    # Save the map to the file
    m.save(STATIC_MAP_FILE)

    # Render the trail map template
    return render_template('trail_map.html', map_file=STATIC_MAP_FILE)

  # On GET request, render the index.html
  return render_template('index.html')


# Run the Flask app
if __name__ == '__main__':
  app.run(host='0.0.0.0', port=80)
