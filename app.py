import sys
path = '/home/dariaomelkina/.virtualenvs/myvirtualenv'
if path not in sys.path:
    sys.path.append(path)

import folium
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from flask import Flask, render_template, request
import json
geolocator = Nominatim(user_agent="specify_your_app_name_here", timeout=3)
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=2, max_retries=4)


app = Flask(__name__)


def read_file(path):
    """
    () -> dict
    Return data from the json file.
    """
    with open(path) as file:
        data1 = file.read()
    data = json.loads(data1, encoding=None, cls=None, object_hook=None, parse_float=None, parse_int=None,
                      parse_constant=None,
                      object_pairs_hook=None)
    return data


def generate_tuples(x):
    """
    Ruterns a list of tuples with name of the friend and his/her location.
    """
    lst = []
    for i in x['users']:
        name = i['screen_name']
        location = i['location']
        lst.append((name, location))
    return lst


def make_map(path):
    my_map = folium.Map(tiles='Stamen Terrain')
    fg_friends = folium.FeatureGroup(name="Friends")
    data = read_file(path)
    my_tuples = generate_tuples(data)
    for i in my_tuples:
        try:
            location_geo = geolocator.geocode(i[1], timeout=5)
            latitude_geo, longitude_geo = location_geo.latitude, location_geo.longitude
            fg_friends.add_child(folium.CircleMarker(location=(latitude_geo, longitude_geo),
                                                    radius=10,
                                                    popup=i[0],
                                                    fill_color='yellow',
                                                    color='blue',
                                                    fill_opacity=0.6))
        except:
            continue
    my_map.add_child(fg_friends)
    my_map.add_child(folium.LayerControl())
    my_map.save('templates/Map.html')


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/map", methods=["POST"])
def web_map():
    path = request.form.get("name")
    if not path:
        return 'failure'
    make_map(path)
    return render_template("Map.html")


if __name__ == '__main__':
    app.run()
