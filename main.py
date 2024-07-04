import os
from flask import Flask, render_template, request
from mapbox import Directions
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
mapbox_token = os.getenv('MAPBOX_TOKEN')
directions = Directions(access_token=mapbox_token)

from helpers import generate_trail

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        start_location = request.form['start_location']
        distance = float(request.form['distance'])
        unit = request.form['unit']
        dest = request.form['dest']
        path_type = request.form['dir']
        # avoid_ferries = 'avoid_ferries' in request.form
        trail_links = generate_trail(start_location, distance, unit, dest, dir)
        button_names = ["Open Your Route"]
        icon_paths = ["static/icons/GoogleMaps.png"]
        trail_buttons = list(zip(button_names, trail_links, icon_paths))
        return render_template('index.html', trail_buttons=trail_buttons)
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
