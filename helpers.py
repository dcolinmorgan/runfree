import os
import requests
import math
import random
import urllib.parse
import numpy as np
from geopy.geocoders import Nominatim
from geopy.distance import geodesic, distance


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
    response_json = response.json()
    features = response_json['features']
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

    closest_destination = closest_feature['geometry']['coordinates']
    return closest_destination[1], closest_destination[0]


def generate_waypoints(start_lat, start_lng, distance_km, destination_type):

    waypoints = [(start_lat, start_lng)]
    directions = [['N', 'E', 'S', 'W'],['N', 'W', 'S', 'E']]
    directions = random.choice(directions)

    start_index = random.randint(0, len(directions) - 1)
    new_directions = directions[start_index:] + directions[:start_index]
    
    if destination_type is not None:
        destination_lat, destination_lng = find_nearby_destination(
            start_lat, start_lng, destination_type)
        if np.round(destination_lat,3) > np.round(start_lat,3):
            DD = 'N'
        if np.round(destination_lat,3) < np.round(start_lat,3):
            DD = 'S'
        if np.round(destination_lng,3) > np.round(start_lng,3):
            DD = 'E'
        if np.round(destination_lng,3) < np.round(start_lng,3):
            DD = 'W'

    
    for direction in (new_directions):

        prev_lat, prev_lng = waypoints[-1]

        if direction == 'N' and DD != 'N':
            angle = random.uniform(0, 2 * math.pi)
            radius = random.uniform(0.005, 0.02)
            next_lat = prev_lat + radius/111 * math.cos(angle) + 0.01
            next_lng = prev_lng + 0.01
        elif direction == 'S' and DD != 'S':
            angle = random.uniform(0, 2 * math.pi)
            radius = random.uniform(0.005, 0.02)
            next_lat = prev_lat - radius/111 * math.cos(angle) +0.01
            next_lng = prev_lng +0.01
        elif direction == 'E' and DD != 'E':
            angle = random.uniform(0, 2 * math.pi)
            radius = random.uniform(0.005, 0.02)
            next_lng = prev_lng + radius/111 * math.sin(angle) +0.01
            next_lat = prev_lat+0.01
        elif direction == 'W' and DD != 'W':
            angle = random.uniform(0, 2 * math.pi)
            radius = random.uniform(0.005, 0.02)
            next_lng = prev_lng - radius/111 * math.sin(angle)+0.01
            next_lat = prev_lat+0.01

        waypoints.append((next_lat, next_lng))
    return waypoints


def generate_waypoints_arch(start_lat, start_lng, distance, num_turns):
    waypoints = []
    total_distance = 0
    prev_waypoint = (start_lng, start_lat)
    while total_distance < distance:# and num_turns < 4:
        
        response = directions.directions([prev_waypoint, next_waypoint],
                                            profile='mapbox/walking')
        snapped_waypoint = response.geojson(
        )['features'][0]['geometry']['coordinates'][-1]

        distance_meters = response.geojson(
        )['features'][0]['properties']['distance']

        if total_distance + distance_meters / 1000 > distance:
            break

        waypoints.append(f"{snapped_waypoint[1]},{snapped_waypoint[0]}")
        prev_waypoint = (snapped_waypoint[0], snapped_waypoint[1])
        total_distance += distance_meters / 1000
        num_turns += 1

    return waypoints

def random_walk(start_lat, start_lng, steps=10, max_step_size=100):

    path = [(start_lat, start_lng)]
    for _ in range(steps):
        angle = random.uniform(0, 360)
        distance_m = random.uniform(0, max_step_size)
        next_point = distance(kilometers=distance_m/1000).destination(point=path[-1], bearing=angle)
        path.append((next_point.latitude, next_point.longitude))
    
    return path

def calculate_bearing(pointA, pointB):
    """
    Calculate the bearing between two points.
    The formulae used is the following:
    θ = atan2(sin(Δlong).cos(lat2),
              cos(lat1).sin(lat2) − sin(lat1).cos(lat2).cos(Δlong))
    """
    lat1, lon1 = math.radians(pointA[0]), math.radians(pointA[1])
    lat2, lon2 = math.radians(pointB[0]), math.radians(pointB[1])
    dLon = lon2 - lon1
    x = math.sin(dLon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) * math.cos(lat2) * math.cos(dLon))
    bearing = math.atan2(x, y)
    bearing = math.degrees(bearing)
    bearing = (bearing + 360) % 360
    return bearing


def remove_backtracking(waypoints):
    """
    Remove waypoints that cause backtracking.
    """
    optimized_path = [waypoints[0]]  # Start with the first waypoint
    for i in range(1, len(waypoints)-1):
        bearing_to_next = calculate_bearing(waypoints[i], waypoints[i+1])
        bearing_from_prev = calculate_bearing(waypoints[i-1], waypoints[i])
        direction_change = abs(bearing_to_next - bearing_from_prev) % 360
        if direction_change < 135 or direction_change > 225:  # Adjust the threshold as needed
            optimized_path.append(waypoints[i])
    optimized_path.append(waypoints[-1])  # Ensure the destination is included
    return optimized_path


def generate_trail(start_location,
                   distance=10,
                   unit='km',
                   destination_type=None,
                   path_type = 'return'):
    if unit == 'mi':
        distance *= 1.60934  # Convert miles to kilometers

    start_lat, start_lng = geocode_location(start_location)
    if path_type == 'return':
        distance /= 2
        
    waypoints = []
    total_distance = 0
    prev_waypoint = (start_lng, start_lat)
    
    # waypoints = generate_waypoints_arch(start_lat, start_lng, distance, 4)
    
    waypoints = generate_waypoints(start_lat, start_lng, distance, destination_type)
    from collections import OrderedDict
    waypoints = list(OrderedDict.fromkeys(waypoints))
    
    # waypoints = random_walk(start_lat, start_lng, 10, distance)
    
    optimized_waypoints = remove_backtracking(waypoints)

    waypoints = [f"{lat}, {lng}" for lat, lng in waypoints]
    seen = set()
    waypoints = [x for x in waypoints if not (x in seen or seen.add(x))]

    if path_type == 'return':
        waypoints.append(f"{start_lat},{start_lng}")
    

    start_location_encoded = urllib.parse.quote(start_location)
    waypoints_encoded = "|".join(urllib.parse.quote(wp) for wp in waypoints)

    google_maps_link = f"https://www.google.com/maps/dir/?api=1&origin={start_location_encoded}&destination={start_location_encoded}&waypoints={waypoints_encoded}"

    return google_maps_link
